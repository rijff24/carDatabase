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

- **Backend**: Python with Flask web framework
- **Database**: SQLite (with support for different environments)
- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript

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