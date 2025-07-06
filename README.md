# Academic Timetable Generator

A comprehensive web application for automated academic scheduling using Flask, Supabase, and OR-Tools constraint satisfaction algorithms.

## Features

- **Multi-institutional Support**: Manage multiple educational institutions
- **Role-based Access Control**: Admin, Faculty, and Student roles
- **Automated Scheduling**: AI-powered timetable generation using OR-Tools
- **Conflict Resolution**: Intelligent handling of room, teacher, and time conflicts
- **Export Capabilities**: Excel, CSV, and summary reports
- **AI Analytics**: OpenAI-powered schedule analysis and optimization
- **Responsive Design**: Mobile-friendly Bootstrap interface

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database (via Supabase)
- Supabase account
- OpenAI API key (optional, for AI features)

### VS Code Setup

1. **Clone and Open Project**
   ```bash
   git clone <repository-url>
   cd academic-timetable-generator
   code .
   ```

2. **Install Python Extension**
   - Install the Python extension for VS Code
   - The project includes `.vscode/settings.json` with optimal configurations

3. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Mac/Linux)
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file based on `.env.example`:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   OPENAI_API_KEY=sk-your-openai-api-key
   SESSION_SECRET=your-secret-key-here
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

5. **Database Setup**
   ```bash
   # Initialize database tables
   python -c "from app import db; db.create_all()"
   ```

6. **Run Development Server**
   ```bash
   # Using VS Code debugger (recommended)
   # Press F5 or use Run -> Start Debugging
   
   # Or run manually
   python main.py
   ```

### Supabase Configuration

1. **Create Supabase Project**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Create new project
   - Wait for project setup completion

2. **Get Database URL**
   - Go to Project Settings → Database
   - Copy the "Connection string" under "Transaction pooler"
   - Replace `[YOUR-PASSWORD]` with your database password

3. **Get API Keys**
   - Go to Project Settings → API
   - Copy "Project URL" and "anon/public" key

4. **Configure Authentication**
   - Go to Authentication → Settings
   - Configure email templates and providers as needed
   - Ensure "Enable email confirmations" is set according to your needs

## Vercel Deployment

### Prerequisites

- Vercel account
- GitHub repository with your code
- All environment variables configured

### Deployment Steps

1. **Prepare for Deployment**
   ```bash
   # Ensure all dependencies are listed
   pip freeze > requirements.txt
   
   # Commit all changes
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "New Project"
   - Import your GitHub repository
   - Configure environment variables:
     - `DATABASE_URL`
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `OPENAI_API_KEY`
     - `SESSION_SECRET`

3. **Environment Variables in Vercel**
   ```
   DATABASE_URL = postgresql://user:pass@host:port/db
   SUPABASE_URL = https://your-project.supabase.co
   SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIs...
   OPENAI_API_KEY = sk-your-openai-key
   SESSION_SECRET = your-random-secret-key
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build completion
   - Your app will be available at `https://your-app.vercel.app`

### Vercel Configuration Files

The project includes:
- `vercel.json`: Deployment configuration
- `wsgi.py`: WSGI entry point for Vercel
- `requirements.txt`: Python dependencies

## Project Structure

```
academic-timetable-generator/
├── app.py                 # Flask application factory
├── main.py               # Application entry point
├── models.py             # Database models
├── auth.py               # Authentication decorators
├── ai_integration.py     # OpenAI integration
├── supabase_client.py    # Supabase client
├── routes/               # Route blueprints
│   ├── auth_routes.py
│   ├── admin_routes.py
│   ├── timetable_routes.py
│   ├── export_routes.py
│   └── ai_routes.py
├── templates/            # Jinja2 templates
├── static/              # CSS, JS, images
├── scheduler/           # OR-Tools scheduling engine
├── utils/               # Utility functions
├── .vscode/             # VS Code configuration
├── vercel.json          # Vercel deployment config
└── requirements.txt     # Python dependencies
```

## API Keys Setup

### Supabase Keys
1. Project URL: Found in Project Settings → API
2. Anon Key: Public key for client-side operations
3. Database URL: PostgreSQL connection string

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create new API key
3. Copy and store securely

## Troubleshooting

### Authentication Issues
- Verify Supabase URL and keys are correct
- Check Supabase authentication settings
- Ensure email confirmation settings match your needs

### Database Connection
- Verify DATABASE_URL format
- Check Supabase project status
- Ensure database password is correct

### Deployment Issues
- Check Vercel build logs
- Verify all environment variables are set
- Ensure requirements.txt is up to date

### AI Features Not Working
- Verify OPENAI_API_KEY is set
- Check OpenAI account billing status
- Review API usage limits

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Supabase and Vercel documentation
3. Check application logs for specific error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.