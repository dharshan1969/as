# Academic Timetable Generator

## Overview

The Academic Timetable Generator is a comprehensive web application designed to automate and manage academic scheduling for educational institutions. Built with Flask and using constraint satisfaction algorithms for intelligent timetable generation, the system supports multi-institutional deployments with role-based access control.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **Styling**: Bootstrap 5 with dark theme support
- **Icons**: Bootstrap Icons
- **JavaScript**: Vanilla JavaScript with Bootstrap components
- **Responsive Design**: Mobile-first approach with fluid containers

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy with declarative base
- **Authentication**: Supabase Auth integration
- **Session Management**: Flask sessions with secure cookies
- **Blueprint Architecture**: Modular route organization
- **Constraint Solver**: OR-Tools CP-SAT for timetable optimization

### Data Storage Solutions
- **Primary Database**: SQLite (development) with PostgreSQL support
- **Connection Pooling**: SQLAlchemy engine options with pool recycling
- **Session Management**: Flask session storage
- **File Exports**: Excel/CSV generation via pandas

## Key Components

### Authentication & Authorization
- **External Auth Provider**: Supabase for user authentication
- **Role-Based Access**: Three-tier system (admin, faculty, student)
- **Session Validation**: Token-based authentication with automatic refresh
- **Multi-Institution Support**: Institution-scoped data access

### Core Data Models
- **Institution**: Top-level organization entity
- **Department**: Academic divisions within institutions
- **User**: Multi-role user system with institution/department associations
- **Course**: Academic courses with credit and enrollment information
- **Teacher**: Faculty members with availability and workload constraints
- **Room**: Physical spaces with capacity and type classifications
- **TimeSlot**: Discrete time periods for scheduling
- **TimetableEntry**: Generated schedule assignments

### Scheduling Engine
- **Algorithm**: Constraint Satisfaction Problem (CSP) solver
- **Optimization**: OR-Tools CP-SAT for conflict resolution
- **Constraints**: Room capacity, teacher availability, time conflicts
- **Flexibility**: Support for partial schedules and manual adjustments

### Export Capabilities
- **Excel Export**: Formatted spreadsheets with institution branding
- **CSV Export**: Raw data for external processing
- **Summary Reports**: Analytics and utilization statistics

## Data Flow

### Authentication Flow
1. User submits credentials via login form
2. Flask validates input and forwards to Supabase
3. Supabase returns JWT tokens upon successful authentication
4. Session stores tokens and user metadata
5. Subsequent requests validate tokens and maintain session state

### Timetable Generation Flow
1. Admin/Faculty initiates generation request
2. System collects constraints (courses, teachers, rooms, timeslots)
3. Scheduling engine processes CSP with defined constraints
4. Generated solution creates TimetableEntry records
5. Frontend displays optimized schedule with conflict highlighting

### Data Management Flow
- **Create**: Form validation → Database insertion → Session feedback
- **Read**: Query filtering by user permissions → Template rendering
- **Update**: Form validation → Database update → Cache invalidation
- **Delete**: Confirmation dialog → Cascade deletion → Relationship cleanup

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and connection management
- **Supabase**: Authentication and user management service
- **OR-Tools**: Constraint programming solver
- **Pandas**: Data manipulation and export functionality
- **Bootstrap 5**: Frontend framework and components

### Development Dependencies
- **Werkzeug**: WSGI utilities and development server
- **Jinja2**: Template engine for dynamic content
- **Requests**: HTTP client for Supabase API communication

### External Services
- **Supabase Auth**: Handles user registration, authentication, and session management
- **Database**: SQLite for development, PostgreSQL production support

## Deployment Strategy

### Environment Configuration
- **Development**: SQLite database with debug logging
- **Production**: PostgreSQL with connection pooling
- **Session Security**: Environment-based secret key management
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments

### Database Management
- **Migrations**: SQLAlchemy automatic table creation
- **Seeding**: Initial data setup through admin interface
- **Backup**: Institution-scoped data export capabilities

### Scaling Considerations
- **Multi-Institution**: Isolated data per institution
- **Role Separation**: Minimal privilege access patterns
- **Session Efficiency**: Token validation caching
- **Database Optimization**: Query filtering at application level

## Changelog
- July 06, 2025: Initial setup with Flask, Supabase, and OR-Tools
- July 06, 2025: Added Vercel deployment configuration and VS Code compatibility
- July 06, 2025: Integrated OpenAI API for AI-powered timetable analysis and optimization
- July 06, 2025: Enhanced authentication error handling and logging
- July 06, 2025: Created comprehensive deployment documentation

## Recent Changes

### Vercel Deployment Support
- Created `vercel.json` configuration for serverless deployment
- Added `wsgi.py` entry point for Vercel Python runtime
- Configured environment variable mapping for production secrets
- Added `.env.example` for local development setup

### VS Code Integration
- Added `.vscode/settings.json` with Python development optimizations
- Created `.vscode/launch.json` for Flask debugging configuration
- Configured HTML/Jinja2 template support and formatting

### OpenAI Integration
- Implemented `ai_integration.py` with GPT-4o model for timetable analysis
- Added AI routes for conflict detection, room suggestions, and workload optimization
- Created AI analytics templates for visualizing optimization results
- Integrated intelligent scheduling recommendations

### Authentication Improvements  
- Enhanced Supabase client error handling with detailed logging
- Added timeout handling and network error recovery
- Improved email validation and normalization
- Fixed User model instantiation issues

### Database Models
- Complete multi-institutional data model with proper relationships
- Support for teachers, courses, rooms, timeslots, and timetable entries
- Role-based access control with institution-scoped data filtering

## User Preferences

Preferred communication style: Simple, everyday language.
Deployment preference: Vercel with VS Code development environment.
AI features: OpenAI integration for schedule optimization and analysis.