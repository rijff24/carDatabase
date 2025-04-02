# Project Structure

The Car Repair and Sales Tracking Application is organized into a modular structure that follows Flask best practices. This document outlines the organization of the codebase, explaining the purpose of each directory and key file.

## Directory Structure

```
project_root/
├── app/                    # Main application package
│   ├── models/             # Database models/schemas
│   ├── routes/             # Route definitions and view functions
│   ├── templates/          # Jinja2 HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   ├── utils/              # Utility functions and helpers
│   ├── reports/            # Report generation functionality
│   └── __init__.py         # Application factory and extension initialization
├── tests/                  # Test directory
├── report_output/          # Directory for generated reports
├── reports/                # Additional report templates
├── docs/                   # Documentation files
├── config.py               # Configuration settings
├── run.py                  # Application entry point
├── app.py                  # CLI commands for application management
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not tracked in git)
```

## Core Application Package (`app/`)

The main application code is organized in the `app/` package, following a modular structure:

### `app/models/`

Contains SQLAlchemy model definitions that represent database tables:

```
app/models/
├── __init__.py          # Package initialization and imports
├── car.py               # Car model definition
├── dealer.py            # Dealer model definition
├── part.py              # Part model definition
├── repair.py            # Repair model definition
├── repair_provider.py   # RepairProvider model definition
├── sale.py              # Sale model definition
├── stand.py             # Stand model definition
└── user.py              # User model definition
```

Each model file defines a single database table and its relationships with other tables.

### `app/routes/`

Contains route definitions organized by feature:

```
app/routes/
├── __init__.py          # Package initialization
├── main.py              # Main routes (home, dashboard)
├── auth.py              # Authentication routes (login, logout)
├── cars.py              # Car-related routes
├── dealers.py           # Dealer-related routes
├── parts.py             # Part-related routes
├── providers.py         # Provider-related routes
├── repairs.py           # Repair-related routes
├── reports.py           # Report generation routes
└── stands.py            # Stand-related routes
```

Each routes file typically contains route handlers for CRUD operations related to a specific feature.

### `app/templates/`

Contains Jinja2 templates organized by feature:

```
app/templates/
├── base.html            # Base template with common layout
├── index.html           # Landing page template
├── dashboard.html       # Dashboard template
├── auth/                # Authentication-related templates
├── cars/                # Car-related templates
├── dealers/             # Dealer-related templates
├── errors/              # Error page templates
├── parts/               # Part-related templates
├── providers/           # Provider-related templates
├── repairs/             # Repair-related templates
├── reports/             # Report-related templates
└── stands/              # Stand-related templates
```

Templates follow a hierarchical structure with inheritance from the base template.

### `app/static/`

Contains static assets for the frontend:

```
app/static/
├── css/                 # CSS stylesheets
├── js/                  # JavaScript files
├── images/              # Image assets
├── fonts/               # Font files
└── vendor/              # Third-party libraries
```

### `app/utils/`

Contains utility functions and helpers:

```
app/utils/
├── __init__.py          # Package initialization
├── forms.py             # Form definitions
├── validators.py        # Input validation functions
├── errors.py            # Error handling utilities
└── helpers.py           # General utility functions
```

### `app/reports/`

Contains report generation functionality:

```
app/reports/
├── __init__.py          # Package initialization
├── base/                # Base report definitions
├── standard/            # Standard report implementations
└── custom/              # Custom report implementations
```

### `app/__init__.py`

The application factory file that initializes Flask and registers extensions and blueprints.

## Test Directory (`tests/`)

Contains test files organized by feature:

```
tests/
├── conftest.py          # Test configuration and fixtures
├── test_models/         # Model tests
├── test_routes/         # Route tests
└── test_utils/          # Utility function tests
```

## Configuration and Execution Files

- `config.py`: Configuration classes for different environments
- `run.py`: Application entry point for running the app
- `app.py`: CLI commands for application management
- `.env`: Environment variables (not in version control)
- `requirements.txt`: Python dependencies

## Report Output Directory (`report_output/`)

Directory where generated reports are stored:

```
report_output/
├── sales/               # Sales reports
├── inventory/           # Inventory reports
└── performance/         # Performance reports
```

## Database Files

SQLite database files for different environments:

- `data-dev.sqlite`: Development database
- `data-test.sqlite`: Testing database
- `data.sqlite`: Production database (if not overridden)

## Scripts and Utilities

Various scripts for database management and sample data:

- `init_database.py`: Database initialization
- `create_sales_table.py`: Sales table creation
- `add_sample_sales.py`: Sample data generation
- `create_sample_sales.py`: Sample sales data creation
- `create_admin_user.py`: Admin user creation
- `fetch_reports.py`: Report data fetching

## File Organization Principles

The project follows these organizational principles:

1. **Feature-based Organization**: Code is organized by feature (cars, repairs, etc.) rather than by function (models, views, etc.) within each directory
2. **Separation of Concerns**: Clear separation between models, views, and controllers
3. **Modular Design**: Each feature is implemented as a separate module with its own models, routes, and templates
4. **Utility Abstraction**: Common functionality is abstracted into utility functions
5. **Configuration Separation**: Configuration is separated from application code 