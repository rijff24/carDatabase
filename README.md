# Car Repair and Sales Tracking Web Application

A full-stack web application for tracking the entire lifecycle of cars—from purchase through repair to sale.

## Features

- Vehicle management (purchase, repair, sales)
- Repair tracking with service providers
- Parts inventory and usage tracking
- Car stand and dealer management
- Comprehensive reporting
- Financial analysis and profit calculation

## Tech Stack

- **Backend**: Python with Flask (2.2.3) web framework
- **Database**: SQLite with SQLAlchemy ORM (1.4.46)
- **ORM**: SQLAlchemy (1.4.46) with Flask-SQLAlchemy (2.5.1)
- **Migration**: Flask-Migrate (3.1.0) with Alembic (1.15.1)
- **Authentication**: Flask-Login (0.6.2)
- **Forms**: Flask-WTF (0.15.1) and WTForms (2.3.3)
- **Template Engine**: Jinja2 (3.1.6)
- **Frontend**: 
  - HTML with Jinja2 templates
  - CSS with Bootstrap framework
  - JavaScript with jQuery
  - Charts using matplotlib (3.10.1)
- **Testing**: pytest (6.2.5)
- **Environment Configuration**: python-dotenv (0.19.0)

## Installation and Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Application Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd car-sales-tracking
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Initialize the database:

```bash
flask create-db
# Or alternatively run:
python init_db.py
```

5. Run the application:

```bash
flask run
# Or alternatively:
python app.py
```

The application will be available at http://localhost:5000

## Project Structure

```
.
├── app/
│   ├── models/        # Database models
│   ├── routes/        # Route handlers and views
│   ├── static/        # Static assets (CSS, JS, images)
│   ├── templates/     # HTML templates
│   ├── utils/         # Utility functions and forms
│   └── __init__.py    # Application factory
├── .env               # Environment variables
├── app.py             # Application entry point
├── config.py          # Configuration
├── init_db.py         # Database initialization script
└── requirements.txt   # Dependencies
```

## Documentation

The application is thoroughly documented in the `docs/` directory:

1. [Overview](./docs/01-overview.md) - System overview and key features
2. [Technical Stack](./docs/02-technical-stack.md) - Technologies used in the application
3. [Project Structure](./docs/03-project-structure.md) - Organization of project files and directories
4. [Database](./docs/04-database.md) - Database schema, tables, fields and relationships
5. [Business Logic](./docs/05-business-logic.md) - Key calculations and business rules
6. [User Interface](./docs/06-user-interface.md) - Pages, forms and field usage
7. [Reports](./docs/07-reports.md) - Report generation and analytics
8. [Authentication & Security](./docs/08-authentication-security.md) - Authentication, authorization and security
9. [Error Handling](./docs/09-error-handling.md) - Error handling and validation
10. [Maintenance](./docs/10-maintenance.md) - Maintenance tasks and procedures
11. [API Reference](./docs/11-api-reference.md) - API endpoints and usage
12. [File Reference](./docs/12-file-reference.md) - Detailed documentation for each file

For more information on how to use the documentation, see the [Documentation README](./docs/README.md).

## Environment Configuration

The application supports three environments:
- Development (default)
- Testing
- Production

Configuration is done through the `.env` file and `config.py`. Each environment uses a separate SQLite database file.

## Usage

1. Log in using the admin credentials (username: admin, password: admin123)
2. Start by adding stands, dealers, and repair providers
3. Add cars as they are purchased
4. Track repairs and parts used
5. Move cars to stands when ready for sale
6. Record sales and view reports

## Reporting System

The application includes a comprehensive reporting system with various report types:

### Sales Performance Report

The Sales Performance Report provides detailed insights into sales metrics, trends, and dealer performance. You can generate this report using the dedicated script:

```bash
# Generate a monthly sales performance report for the current year
python generate_sales_report.py --period monthly --year 2024

# Generate a quarterly report with JSON output
python generate_sales_report.py --period quarterly --year 2023 --format json

# Generate a yearly report with CSV output and visualization
python generate_sales_report.py --period yearly --year 2023 --format csv --chart
```

#### Available options:

- `--period`: Reporting period (monthly, quarterly, yearly)
- `--year`: Year to report on (defaults to current year)
- `--format`: Output format (console, json, csv)
- `--output`: Custom output file path
- `--chart`: Generate a visual chart of the data
- `--chart-file`: Custom chart output file path

The generated reports include:
- Summary metrics (total sales, revenue, profit, margins)
- Period-by-period breakdown
- Dealer performance comparison
- Top-selling models
- Year-over-year comparisons
- Visual charts (when requested)

Reports can be saved in various formats for integration with other tools or for presentation purposes.

## Available Commands

```bash
# Create database tables
flask create-db

# Drop all database tables
flask drop-db

# Create admin user
flask create-admin
```

## License

[MIT License](LICENSE) 