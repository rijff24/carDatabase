# Technical Stack

The Car Repair and Sales Tracking Application is built using the following technologies:

## Backend Technologies

### Primary Framework
- **Python Flask**: A lightweight WSGI web application framework
  - Version: 2.0.1+
  - Used for routing, request handling, and application structure

### Database
- **SQLite**: Self-contained, serverless SQL database engine
  - Used for data storage in development, testing, and production environments
  - Separate database files for different environments:
    - `data-dev.sqlite`: Development database
    - `data-test.sqlite`: Testing database
    - `data.sqlite`: Production database (unless overridden)

### ORM (Object Relational Mapper)
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping (ORM) library
  - Version: 1.4+
  - Used for database operations and model definitions
  - Provides abstraction layer between Python objects and database

### Database Migration
- **Flask-Migrate**: SQLAlchemy database migrations for Flask using Alembic
  - Used to manage database schema changes
  - Maintains version control for database schema

### Authentication
- **Flask-Login**: User session management for Flask
  - Handles user authentication and session management
  - Provides user authentication state and protection for routes

### Security
- **Werkzeug**: Comprehensive WSGI web application library
  - Used for password hashing and security functions
  - Provides security utilities like password hashing with salt

### Environment Management
- **python-dotenv**: Loads environment variables from .env files
  - Used to manage configuration in different environments
  - Helps keep sensitive information out of version control

## Frontend Technologies

### Templating
- **Jinja2**: Template engine for Python
  - Used for rendering HTML templates
  - Provides template inheritance, filters, and macros

### CSS Framework
- **Bootstrap**: Front-end toolkit for responsive design
  - Used for styling and responsive layout
  - Provides consistent UI components and grid system

### JavaScript Libraries
- **jQuery**: Fast, small, and feature-rich JavaScript library
  - Used for DOM manipulation and AJAX requests
  - Simplifies client-side scripting
- **Chart.js**: JavaScript charting library
  - Used for creating interactive charts in reports
  - Provides visualizations for analytics data

### Mobile JavaScript Features
- **Mobile Device Detection**: Automatic detection of mobile devices and touch capabilities
- **Touch Gesture Support**: Swipe gestures for navigation (left/right swipe to open/close menu)
- **Enhanced Mobile Navigation**: Improved hamburger menu with touch-friendly interactions
- **Mobile Table Enhancement**: Automatic conversion to mobile-friendly stacked layout
- **Touch Feedback**: Visual feedback for button and card interactions on touch devices
- **Mobile Form Optimization**: Auto-scroll to focused inputs and enhanced keyboard handling
- **Orientation Change Handling**: Automatic layout adjustments on device rotation
- **Viewport Management**: Dynamic viewport height calculation and mobile keyboard handling

## Development and Testing Tools

### Testing Framework
- **pytest**: Testing framework for Python
  - Used for unit and integration testing
  - Supports test fixtures and mocking

### Code Quality
- **flake8**: Python code linting tool
  - Enforces PEP 8 style guide
  - Helps maintain code quality

### Development Server
- **Werkzeug**: Provides development server for local testing
  - Used in development for auto-reloading and debugging

## Deployment Configuration

The application can be deployed in various environments:

### Development Environment
- Local development server
- Debug mode enabled
- SQLite database (`data-dev.sqlite`)
- Detailed error reporting
- Auto-reloading for code changes

### Testing Environment
- Separate testing configuration
- SQLite test database (`data-test.sqlite`)
- Test-specific settings
- No email sending

### Production Environment
- Production-grade WSGI server (e.g., Gunicorn)
- Error logging to file
- SQLite database (`data.sqlite`) or configurable via DATABASE_URL
- Email notifications for errors
- Security optimizations

## External Integrations

The application is designed to potentially integrate with:

- **Email Services**: For sending notifications and reports
- **File Storage Systems**: For storing report outputs and backups
- **Authentication Providers**: For advanced authentication options
- **Payment Processing Systems**: For handling financial transactions

## Dependency Management

Dependencies are managed via:

- **requirements.txt**: Lists all Python package dependencies with versions
- **pip**: Python package manager for installing dependencies

## Version Control

- **Git**: Used for version control and code management
- **.gitignore**: Configured to exclude environment-specific files and sensitive data 