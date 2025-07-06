import os
import requests
import json
from typing import Optional, Dict, Any

class SupabaseClient:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL", "")
        self.key = os.environ.get("SUPABASE_ANON_KEY", "")
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
    
    def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        """Sign up a new user"""
        url = f"{self.url}/auth/v1/signup"
        data = {
            "email": email.strip().lower(),
            "password": password
        }
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": {
                        "message": f"Signup failed: {response.text}",
                        "status_code": response.status_code
                    }
                }
        except requests.exceptions.RequestException as e:
            return {
                "error": {
                    "message": f"Network error: {str(e)}"
                }
            }
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in an existing user"""
        url = f"{self.url}/auth/v1/token?grant_type=password"
        data = {
            "email": email.strip().lower(),
            "password": password
        }
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": {
                        "message": f"Login failed: {response.text}",
                        "status_code": response.status_code
                    }
                }
        except requests.exceptions.RequestException as e:
            return {
                "error": {
                    "message": f"Network error: {str(e)}"
                }
            }
    
    def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out user"""
        url = f"{self.url}/auth/v1/logout"
        headers = {**self.headers, "Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers)
        return response.json() if response.content else {}
    
    def get_user(self, access_token: str) -> Dict[str, Any]:
        """Get user info from access token"""
        url = f"{self.url}/auth/v1/user"
        headers = {**self.headers, "Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        return response.json()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        url = f"{self.url}/auth/v1/token?grant_type=refresh_token"
        data = {"refresh_token": refresh_token}
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

# Global instance
supabase_client = SupabaseClient()
