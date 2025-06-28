# File Reference

This document provides a reference for the key files in the Car Repair and Sales Tracking Application.

## Application Structure

The application is organized into the following directories:

- `app/` - Main application code
- `migrations/` - Database migration scripts
- `tests/` - Test files
- `docs/` - Documentation
- `config/` - Configuration files
- `scripts/` - Utility scripts

## Core Application Files

| File | Description |
|------|-------------|
| `run.py` | Application entry point for starting the server |
| `config.py` | Configuration settings for different environments |
| `requirements.txt` | Python package dependencies |
| `.env` | Environment variables (not in source control) |
| `.gitignore` | Git ignore patterns |

## Core Application Module

| File | Description |
|------|-------------|
| `app/__init__.py` | Application factory and extension initialization |
| `app/errors.py` | Global error handlers |
| `app/decorators.py` | Custom decorators (e.g., role requirements) |

## Models

| File | Description |
|------|-------------|
| `app/models/base.py` | Base model utilities and exceptions |
| `app/models/user.py` | User model for authentication |
| `app/models/car.py` | Vehicle inventory model |
| `app/models/repair.py` | Vehicle repair model |
| `app/models/sale.py` | Sales transaction model |
| `app/models/dealer.py` | Dealer information model |
| `app/models/stand.py` | Display stand model |
| `app/models/part.py` | Repair part model |
| `app/models/repair_part.py` | Association between repairs and parts |
| `app/models/repair_provider.py` | Repair service provider model |

## Blueprints and Routes

### Authentication

| File | Description |
|------|-------------|
| `app/auth/__init__.py` | Auth blueprint definition |
| `app/auth/routes.py` | Authentication routes (login, logout, etc.) |
| `app/auth/forms.py` | Authentication forms |

### Main

| File | Description |
|------|-------------|
| `app/main/__init__.py` | Main blueprint definition |
| `app/main/routes.py` | Main routes including dashboard |
| `app/main/views.py` | View handlers for main routes |

### Inventory Management

| File | Description |
|------|-------------|
| `app/inventory/__init__.py` | Inventory blueprint definition |
| `app/inventory/routes.py` | Inventory management routes |
| `app/inventory/forms.py` | Inventory forms (add/edit vehicles, stands) |

### Repair Management

| File | Description |
|------|-------------|
| `app/repairs/__init__.py` | Repairs blueprint definition |
| `app/repairs/routes.py` | Repair management routes |
| `app/repairs/forms.py` | Repair forms (create/edit repairs, parts) |

### Sales Management

| File | Description |
|------|-------------|
| `app/sales/__init__.py` | Sales blueprint definition |
| `app/sales/routes.py` | Sales management routes |
| `app/sales/forms.py` | Sales forms (record sales) |

### Reporting

| File | Description |
|------|-------------|
| `app/reports/__init__.py` | Reports blueprint definition |
| `app/reports/routes.py` | Report generation routes |
| `app/reports/forms.py` | Report configuration forms |
| `app/reports/generators.py` | Report generation logic |

### API

| File | Description |
|------|-------------|
| `app/api/__init__.py` | API blueprint definition |
| `app/api/routes.py` | API endpoints |
| `app/api/auth.py` | API authentication |
| `app/api/schemas.py` | Request/response schemas |

## Utilities

| File | Description |
|------|-------------|
| `app/utils/logging.py` | Action and error logging |
| `app/utils/validation.py` | Data validation helpers |
| `app/utils/export.py` | Data export utilities |
| `app/utils/reports.py` | Report generation helpers |
| `app/utils/email.py` | Email sending utilities |
| `app/utils/security.py` | Security helpers |

## Templates

### Layouts

| File | Description |
|------|-------------|
| `app/templates/base.html` | Main application layout with mobile optimization |
| `app/templates/error.html` | Error page layout |
| `app/templates/print.html` | Printable page layout |

#### Base Template Mobile Features

The `base.html` template includes comprehensive mobile optimizations:

- **Responsive Viewport**: Proper viewport meta tag for mobile devices
- **Mobile Navigation**: Enhanced hamburger menu with touch-friendly interactions
- **Flash Messages**: Mobile-optimized alert styling with improved spacing
- **Footer Enhancement**: Mobile-specific footer with usage hints
- **Dark Mode Support**: Mobile-compatible dark mode with proper contrast
- **Safe Area Support**: iOS safe area insets for proper display on devices with notches
- **Touch Feedback**: Visual feedback for touch interactions
- **Mobile Classes**: Automatic addition of mobile-specific CSS classes

### Auth Templates

| File | Description |
|------|-------------|
| `app/templates/auth/login.html` | Login form |
| `app/templates/auth/register.html` | User registration form |
| `app/templates/auth/reset_password.html` | Password reset form |
| `app/templates/auth/profile.html` | User profile |
| `app/templates/auth/users.html` | User management (admin) |

### Main Templates

| File | Description |
|------|-------------|
| `app/templates/main/dashboard.html` | Main dashboard |
| `app/templates/main/index.html` | Landing page |

### Inventory Templates

| File | Description |
|------|-------------|
| `app/templates/inventory/index.html` | Inventory listing |
| `app/templates/inventory/add_car.html` | Add vehicle form |
| `app/templates/inventory/edit_car.html` | Edit vehicle form |
| `app/templates/inventory/view_car.html` | Vehicle details |
| `app/templates/inventory/stands.html` | Display stand management |

### Repair Templates

| File | Description |
|------|-------------|
| `app/templates/repairs/index.html` | Repairs listing |
| `app/templates/repairs/add_repair.html` | Add repair form |
| `app/templates/repairs/edit_repair.html` | Edit repair form |
| `app/templates/repairs/view_repair.html` | Repair details |
| `app/templates/repairs/parts.html` | Parts management |
| `app/templates/repairs/providers.html` | Repair provider management |

### Sales Templates

| File | Description |
|------|-------------|
| `app/templates/sales/index.html` | Sales listing |
| `app/templates/sales/record_sale.html` | Record sale form |
| `app/templates/sales/view_sale.html` | Sale details |
| `app/templates/sales/dealers.html` | Dealer management |

### Report Templates

| File | Description |
|------|-------------|
| `app/templates/reports/index.html` | Reports dashboard |
| `app/templates/reports/financial.html` | Financial reports |
| `app/templates/reports/inventory.html` | Inventory reports |
| `app/templates/reports/sales.html` | Sales performance reports |
| `app/templates/reports/repairs.html` | Repair efficiency reports |
| `app/templates/reports/custom.html` | Custom report builder |

## Static Assets

### CSS

| File | Description |
|------|-------------|
| `app/static/css/style.css` | Main application styles |
| `app/static/css/print.css` | Print-specific styles |

### JavaScript

| File | Description |
|------|-------------|
| `app/static/js/app.js` | Main application scripts |
| `app/static/js/charts.js` | Chart generation |
| `app/static/js/forms.js` | Form handling |
| `app/static/js/validation.js` | Client-side validation |

## Test Files

| File | Description |
|------|-------------|
| `tests/conftest.py` | Test configuration and fixtures |
| `tests/test_models.py` | Unit tests for models |
| `tests/test_routes.py` | Unit tests for routes |
| `tests/test_api.py` | API tests |
| `tests/test_integration.py` | Integration tests |
| `tests/test_utils.py` | Utility function tests |

## Database Migration Files

| File | Description |
|------|-------------|
| `migrations/env.py` | Migration environment setup |
| `migrations/script.py.mako` | Migration script template |
| `migrations/versions/` | Migration script versions |

## Utility Scripts

| File | Description |
|------|-------------|
| `scripts/generate_sample_data.py` | Create sample data for development |
| `scripts/backup_database.py` | Database backup utility |
| `scripts/db_cleanup.py` | Database maintenance |
| `scripts/generate_reports.py` | Generate scheduled reports 