# Overview

This is a Flask-based olive oil mill management system (Frantoio Oleario) designed to track and manage customer information and olive oil milling operations. The application provides a web interface for managing customers, scheduling and tracking milling sessions (moliture), and generating reports. The system handles the complete workflow from customer registration to milling completion with state tracking and PDF report generation capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Flask with Jinja2 templating engine
- **UI Framework**: Bootstrap 5 with dark theme for responsive design
- **JavaScript**: Vanilla JavaScript for client-side interactions including form validation, auto-formatting, and dynamic content loading
- **Static Assets**: Organized structure with separate CSS and JavaScript files
- **Icons**: Bootstrap Icons for consistent iconography throughout the interface

## Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Application Structure**: Modular design with separate files for routes, models, and utility functions
- **Database ORM**: SQLAlchemy with DeclarativeBase for modern type support
- **Session Management**: Flask sessions with configurable secret key
- **Middleware**: ProxyFix middleware for proper header handling in deployment environments

## Data Model
- **Cliente (Customer)**: Stores customer information including contact details and notes
- **Molitura (Milling)**: Tracks milling operations with state management (accettazione, in molitura, completa, archiviata)
- **Cassone (Container)**: Referenced in models but not fully implemented, likely for tracking olive containers
- **Relationships**: One-to-many relationship between customers and milling operations with cascade delete

## State Management
- **Milling States**: Four-stage workflow from acceptance to archival
- **Section Assignment**: Milling operations assigned to specific sections (1-4)
- **Timestamp Tracking**: Creation and operation timestamps for audit trails

## Report Generation
- **PDF Generation**: ReportLab library for creating formatted PDF reports
- **Report Types**: Milling operation reports with customer and operation details
- **Layout**: A4 format with professional styling and company branding

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and query builder
- **Werkzeug**: WSGI utilities and middleware

## Frontend Dependencies
- **Bootstrap 5**: CSS framework loaded via CDN with dark theme
- **Bootstrap Icons**: Icon library for UI elements

## PDF Generation
- **ReportLab**: PDF document generation library for creating formatted reports

## Database
- **SQLite**: Default database engine with configurable DATABASE_URL for other database systems
- **Connection Pooling**: Configured with pool recycling and health checks for production reliability

## Development Tools
- **Python Logging**: Configured for debug-level logging during development
- **Flask Debug Mode**: Enabled for development with hot reloading