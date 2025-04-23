# API Reference

This document provides detailed information about the API endpoints available in the Car Repair and Sales Tracking Application.

## API Overview

The application exposes a RESTful API for integration with other systems. The API provides access to various resources including vehicles, repairs, sales, and reporting data.

### Base URL

All API endpoints are relative to the base URL:

```
https://example.com/api/v1
```

### Authentication

API requests require authentication using JWT (JSON Web Tokens):

```
Authorization: Bearer <jwt_token>
```

To obtain a token, use the authentication endpoint:

```
POST /auth/token
```

With request body:

```json
{
  "username": "api_user",
  "password": "secure_password",
  "client_id": "your_client_id"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Response Format

All API responses follow a consistent format:

#### Success Response

```json
{
  "status": "success",
  "data": {
    // Resource-specific data
  },
  "meta": {
    // Pagination, filtering, or other metadata
  }
}
```

#### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { /* Additional error details */ }
  }
}
```

## Vehicles API

### Get Vehicle List

Retrieves a list of vehicles.

```
GET /vehicles
```

**Query Parameters**:

| Parameter    | Type   | Description                       |
|--------------|--------|-----------------------------------|
| status       | string | Filter by vehicle status          |
| make         | string | Filter by vehicle make            |
| limit        | int    | Maximum number of results         |
| offset       | int    | Offset for pagination             |
| sort         | string | Field to sort by                  |
| sort_dir     | string | Sort direction (asc or desc)      |

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "car_id": 1,
      "vehicle_name": "2018 Toyota Camry",
      "vehicle_make": "Toyota",
      "vehicle_model": "Camry",
      "purchase_price": 15000.00,
      "sale_price": 19500.00,
      "date_bought": "2023-01-15",
      "date_sold": "2023-02-20",
      "repair_status": "Sold",
      "profit": 4500.00,
      "total_repair_cost": 0.00,
      "links": {
        "self": "/api/v1/vehicles/1",
        "repairs": "/api/v1/vehicles/1/repairs",
        "sale": "/api/v1/vehicles/1/sale"
      }
    },
    // Additional vehicles...
  ],
  "meta": {
    "total": 125,
    "limit": 20,
    "offset": 0,
    "next": "/api/v1/vehicles?limit=20&offset=20",
    "previous": null
  }
}
```

### Get Vehicle Detail

Retrieves details for a specific vehicle.

```
GET /vehicles/{car_id}
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| car_id    | int  | ID of the vehicle  |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "car_id": 1,
    "vehicle_name": "2018 Toyota Camry",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_year": 2018,
    "purchase_price": 15000.00,
    "sale_price": 19500.00,
    "date_bought": "2023-01-15",
    "date_sold": "2023-02-20",
    "repair_status": "Sold",
    "current_location": "Main Showroom",
    "stand_id": 3,
    "refuel_cost": 50.00,
    "dealer_id": 2,
    "profit": 4500.00,
    "profit_margin": 23.08,
    "days_in_recon": 12,
    "days_on_stand": 24,
    "total_repair_cost": 0.00,
    "total_investment": 15050.00,
    "repairs": [
      {
        "repair_id": 5,
        "description": "Oil change and inspection",
        "repair_cost": 0.00,
        "start_date": "2023-01-16",
        "end_date": "2023-01-16"
      }
    ],
    "links": {
      "self": "/api/v1/vehicles/1",
      "repairs": "/api/v1/vehicles/1/repairs",
      "sale": "/api/v1/vehicles/1/sale"
    }
  }
}
```

### Create Vehicle

Creates a new vehicle record.

```
POST /vehicles
```

**Request Body**:

```json
{
  "vehicle_name": "2019 Honda Accord",
  "vehicle_make": "Honda",
  "vehicle_model": "Accord",
  "year": 2019,
  "colour": "Silver",
  "dekra_condition": "Good",
  "licence_number": "ABC123",
  "registration_number": "DEF456",
  "purchase_price": 16500.00,
  "source": "Auction",
  "current_location": "Warehouse",
  "repair_status": "Waiting for Repairs",
  "refuel_cost": 60.00
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "car_id": 126,
    "vehicle_name": "2019 Honda Accord",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "year": 2019,
    "colour": "Silver",
    "dekra_condition": "Good",
    "licence_number": "ABC123",
    "registration_number": "DEF456",
    "purchase_price": 16500.00,
    "source": "Auction",
    "current_location": "Warehouse",
    "repair_status": "Waiting for Repairs",
    "refuel_cost": 60.00,
    "links": {
      "self": "/api/v1/vehicles/126"
    }
  }
}
```

### Update Vehicle

Updates an existing vehicle record.

```
PUT /vehicles/{car_id}
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| car_id    | int  | ID of the vehicle  |

**Request Body**:

```json
{
  "current_location": "Service Bay",
  "repair_status": "In Repair",
  "refuel_cost": 75.00
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "car_id": 126,
    "vehicle_name": "2019 Honda Accord",
    "current_location": "Service Bay",
    "repair_status": "In Repair",
    "refuel_cost": 75.00,
    "links": {
      "self": "/api/v1/vehicles/126"
    }
  }
}
```

### Delete Vehicle

Deletes a vehicle record.

```
DELETE /vehicles/{car_id}
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| car_id    | int  | ID of the vehicle  |

**Response**:

```json
{
  "status": "success",
  "data": {
    "message": "Vehicle deleted successfully"
  }
}
```

## Repairs API

### Get Repairs List

Retrieves a list of repairs.

```
GET /repairs
```

**Query Parameters**:

| Parameter    | Type   | Description                       |
|--------------|--------|-----------------------------------|
| car_id       | int    | Filter by vehicle ID              |
| status       | string | Filter by repair status           |
| provider_id  | int    | Filter by repair provider         |
| limit        | int    | Maximum number of results         |
| offset       | int    | Offset for pagination             |

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "repair_id": 5,
      "car_id": 1,
      "provider_id": 3,
      "repair_type": "Maintenance",
      "description": "Oil change and inspection",
      "start_date": "2023-01-16",
      "end_date": "2023-01-16",
      "repair_cost": 0.00,
      "status": "Completed",
      "links": {
        "self": "/api/v1/repairs/5",
        "car": "/api/v1/vehicles/1",
        "provider": "/api/v1/providers/3"
      }
    },
    // Additional repairs...
  ],
  "meta": {
    "total": 45,
    "limit": 20,
    "offset": 0
  }
}
```

### Get Repair Detail

Retrieves details for a specific repair.

```
GET /repairs/{repair_id}
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| repair_id | int  | ID of the repair   |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "repair_id": 5,
    "car_id": 1,
    "provider_id": 3,
    "repair_type": "Maintenance",
    "description": "Oil change and inspection",
    "start_date": "2023-01-16",
    "end_date": "2023-01-16",
    "repair_cost": 0.00,
    "status": "Completed",
    "notes": "Routine maintenance",
    "parts": [
      {
        "part_id": 7,
        "name": "Oil Filter",
        "quantity": 1,
        "unit_cost": 15.00,
        "total_cost": 15.00
      },
      {
        "part_id": 12,
        "name": "Engine Oil (5W-30)",
        "quantity": 5,
        "unit_cost": 10.00,
        "total_cost": 50.00
      }
    ],
    "links": {
      "self": "/api/v1/repairs/5",
      "car": "/api/v1/vehicles/1",
      "provider": "/api/v1/providers/3"
    }
  }
}
```

### Create Repair

Creates a new repair record.

```
POST /repairs
```

**Request Body**:

```json
{
  "car_id": 126,
  "provider_id": 3,
  "repair_type": "Mechanical",
  "description": "Brake pad replacement",
  "start_date": "2023-06-15",
  "repair_cost": 350.00,
  "status": "Pending",
  "notes": "Front brakes only"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "repair_id": 46,
    "car_id": 126,
    "provider_id": 3,
    "repair_type": "Mechanical",
    "description": "Brake pad replacement",
    "start_date": "2023-06-15",
    "repair_cost": 350.00,
    "status": "Pending",
    "notes": "Front brakes only",
    "links": {
      "self": "/api/v1/repairs/46",
      "car": "/api/v1/vehicles/126",
      "provider": "/api/v1/providers/3"
    }
  }
}
```

## Sales API

### Get Sales List

Retrieves a list of sales.

```
GET /sales
```

**Query Parameters**:

| Parameter    | Type   | Description                       |
|--------------|--------|-----------------------------------|
| car_id       | int    | Filter by vehicle ID              |
| dealer_id    | int    | Filter by dealer ID               |
| start_date   | date   | Filter by sales after this date   |
| end_date     | date   | Filter by sales before this date  |
| limit        | int    | Maximum number of results         |
| offset       | int    | Offset for pagination             |

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "sale_id": 25,
      "car_id": 1,
      "dealer_id": 2,
      "sale_price": 19500.00,
      "sale_date": "2023-02-20",
      "payment_method": "Finance",
      "profit": 4500.00,
      "profit_margin": 23.08,
      "links": {
        "self": "/api/v1/sales/25",
        "car": "/api/v1/vehicles/1",
        "dealer": "/api/v1/dealers/2"
      }
    },
    // Additional sales...
  ],
  "meta": {
    "total": 67,
    "limit": 20,
    "offset": 0
  }
}
```

### Create Sale

Creates a new sale record.

```
POST /sales
```

**Request Body**:

```json
{
  "car_id": 126,
  "dealer_id": 2,
  "sale_price": 22500.00,
  "sale_date": "2023-06-30",
  "payment_method": "Cash",
  "customer_name": "John Smith",
  "customer_contact": "john.smith@example.com",
  "notes": "Repeat customer"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "sale_id": 68,
    "car_id": 126,
    "dealer_id": 2,
    "sale_price": 22500.00,
    "sale_date": "2023-06-30",
    "payment_method": "Cash",
    "customer_name": "John Smith",
    "customer_contact": "john.smith@example.com",
    "notes": "Repeat customer",
    "profit": 5925.00,
    "profit_margin": 26.33,
    "links": {
      "self": "/api/v1/sales/68",
      "car": "/api/v1/vehicles/126",
      "dealer": "/api/v1/dealers/2"
    }
  }
}
```

## Settings API

### Get All Settings

Retrieves all application settings.

```
GET /settings
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "stand_aging_threshold_days": 180,
    "status_inactivity_threshold_days": 30,
    "enable_depreciation_tracking": false,
    "enable_status_warnings": true,
    "enable_subform_dropdowns": true,
    "enable_dark_mode": false
  }
}
```

### Get Setting By Key

Retrieves a specific setting by its key.

```
GET /settings/{key}
```

**Path Parameters**:

| Parameter | Type   | Description        |
|-----------|--------|--------------------|
| key       | string | Setting key        |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "key": "stand_aging_threshold_days",
    "value": 180,
    "type": "int",
    "description": "Number of days after which a car on a stand is considered aging"
  }
}
```

### Update Setting

Updates a specific setting value.

```
PUT /settings/{key}
```

**Path Parameters**:

| Parameter | Type   | Description        |
|-----------|--------|--------------------|
| key       | string | Setting key        |

**Request Body**:

```json
{
  "value": 90,
  "description": "Number of days after which a car on a stand is considered aging"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "key": "stand_aging_threshold_days",
    "value": 90,
    "type": "int",
    "description": "Number of days after which a car on a stand is considered aging"
  }
}
```

## Vehicle Data API

### Get Makes List

Retrieves a list of vehicle makes.

```
GET /vehicle-data/makes
```

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Toyota"
    },
    {
      "id": 2,
      "name": "Honda"
    },
    {
      "id": 3,
      "name": "Ford"
    }
    // Additional makes...
  ]
}
```

### Create Make

Creates a new vehicle make.

```
POST /vehicle-data/makes
```

**Request Body**:

```json
{
  "name": "Mazda"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "Mazda"
  }
}
```

### Get Models by Make

Retrieves models for a specific make.

```
GET /vehicle-data/makes/{make_id}/models
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| make_id   | int  | ID of the make     |

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Camry",
      "make_id": 1
    },
    {
      "id": 2,
      "name": "Corolla",
      "make_id": 1
    },
    {
      "id": 3,
      "name": "RAV4",
      "make_id": 1
    }
    // Additional models...
  ]
}
```

### Create Model

Creates a new vehicle model for a specific make.

```
POST /vehicle-data/makes/{make_id}/models
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| make_id   | int  | ID of the make     |

**Request Body**:

```json
{
  "name": "Prius"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "Prius",
    "make_id": 1
  }
}
```

### Get Colors List

Retrieves a list of vehicle colors.

```
GET /vehicle-data/colors
```

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Black"
    },
    {
      "id": 2,
      "name": "White"
    },
    {
      "id": 3,
      "name": "Silver"
    }
    // Additional colors...
  ]
}
```

### Create Color

Creates a new vehicle color.

```
POST /vehicle-data/colors
```

**Request Body**:

```json
{
  "name": "Blue"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "id": 4,
    "name": "Blue"
  }
}
```

## Import API

### Get Import Templates

Retrieves a list of available import templates.

```
GET /import/templates
```

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "entity_type": "cars",
      "description": "Vehicle import template",
      "download_url": "/api/v1/import/templates/cars"
    },
    {
      "entity_type": "repairs",
      "description": "Repairs import template",
      "download_url": "/api/v1/import/templates/repairs"
    },
    {
      "entity_type": "sales",
      "description": "Sales import template",
      "download_url": "/api/v1/import/templates/sales"
    },
    {
      "entity_type": "dealers",
      "description": "Dealers import template",
      "download_url": "/api/v1/import/templates/dealers"
    },
    {
      "entity_type": "parts",
      "description": "Parts import template",
      "download_url": "/api/v1/import/templates/parts"
    },
    {
      "entity_type": "stands",
      "description": "Stands import template",
      "download_url": "/api/v1/import/templates/stands"
    }
  ]
}
```

### Download Import Template

Downloads a specific import template.

```
GET /import/templates/{entity_type}
```

**Path Parameters**:

| Parameter   | Type   | Description                       |
|-------------|--------|-----------------------------------|
| entity_type | string | Type of entity (cars, repairs, etc.) |

**Response**: Excel file download

### Import Data

Imports data for a specific entity type.

```
POST /import/{entity_type}
```

**Path Parameters**:

| Parameter   | Type   | Description                       |
|-------------|--------|-----------------------------------|
| entity_type | string | Type of entity (cars, repairs, etc.) |

**Request**: Form data with file upload

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "imported": 15,
    "failed": 2,
    "errors": [
      "Row 3: Missing required field 'VIN'",
      "Row 8: Invalid make 'Toyotta'"
    ]
  }
}
```

## Reports API

### Get Available Reports

Retrieves a list of available reports.

```
GET /reports
```

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "id": "profit_and_loss",
      "name": "Profit and Loss Report",
      "category": "Financial",
      "description": "Provides a comprehensive view of business financial performance",
      "endpoints": {
        "generate": "/api/v1/reports/profit_and_loss",
        "export": "/api/v1/reports/profit_and_loss/export"
      }
    },
    // Additional reports...
  ]
}
```

### Generate Report

Generates a specific report.

```
GET /reports/{report_id}
```

**Path Parameters**:

| Parameter | Type   | Description    |
|-----------|--------|----------------|
| report_id | string | ID of report   |

**Query Parameters**: Vary by report type

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "report_id": "profit_and_loss",
    "generated_at": "2023-06-15T14:30:00Z",
    "parameters": {
      "start_date": "2023-01-01",
      "end_date": "2023-06-01"
    },
    "summary": {
      "total_revenue": 245000.00,
      "total_costs": 175000.00,
      "gross_profit": 70000.00,
      "profit_margin": 28.57
    },
    "details": [
      // Report-specific details...
    ]
  }
}
```

### Export Report

Exports a report in a specific format.

```
GET /reports/{report_id}/export
```

**Path Parameters**:

| Parameter | Type   | Description    |
|-----------|--------|----------------|
| report_id | string | ID of report   |

**Query Parameters**:

| Parameter | Type   | Description                   |
|-----------|--------|-------------------------------|
| format    | string | Export format (pdf, csv, xlsx) |

**Response**: File download in requested format

## User Management API

### Get Users List

Retrieves a list of users.

```
GET /users
```

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "user_id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "is_active": true,
      "last_login": "2023-06-14T10:15:00Z"
    },
    // Additional users...
  ]
}
```

### Create User

Creates a new user.

```
POST /users
```

**Request Body**:

```json
{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "role": "user",
  "full_name": "New User"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "user_id": 5,
    "username": "new_user",
    "email": "user@example.com",
    "role": "user",
    "is_active": true
  }
}
```

## Subform Helper APIs

### Quick Create Dealer

Creates a new dealer from a simplified form.

```
POST /dealers/quick-create
```

**Request Body**:

```json
{
  "name": "New Dealer",
  "contact_name": "John Contact",
  "contact_phone": "555-1234"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "dealer_id": 12,
    "name": "New Dealer",
    "contact_name": "John Contact",
    "contact_phone": "555-1234"
  }
}
```

### Quick Create Provider

Creates a new repair provider from a simplified form.

```
POST /providers/quick-create
```

**Request Body**:

```json
{
  "name": "New Provider",
  "specialization": "Electrical",
  "contact_phone": "555-5678"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "provider_id": 8,
    "name": "New Provider",
    "specialization": "Electrical",
    "contact_phone": "555-5678"
  }
}
```

### Quick Create Part

Creates a new part from a simplified form.

```
POST /parts/quick-create
```

**Request Body**:

```json
{
  "name": "Air Filter",
  "unit_cost": 25.00,
  "supplier": "Auto Parts Inc"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "part_id": 15,
    "name": "Air Filter",
    "unit_cost": 25.00,
    "supplier": "Auto Parts Inc"
  }
}
```

## Helper Functions

### Get Dashboard Summary

Retrieves a summary of key metrics for the dashboard.

```
GET /dashboard/summary
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "inventory_count": 42,
    "vehicles_on_display": 25,
    "vehicles_in_repair": 12,
    "vehicles_waiting": 5,
    "sales_this_month": 8,
    "profit_this_month": 45000.00,
    "average_profit_margin": 21.5,
    "aging_vehicles": 3
  }
}
```

### Check Vehicle Status

Checks the detailed status of a vehicle, including aging and inactivity.

```
GET /vehicles/{car_id}/status-check
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| car_id    | int  | ID of the vehicle  |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "car_id": 126,
    "repair_status": "On Display",
    "days_on_stand": 45,
    "is_aging": false,
    "aging_threshold": 180,
    "has_inactive_status": true,
    "inactivity_threshold": 30,
    "last_status_change": "2023-05-01",
    "recommended_actions": [
      "Review pricing",
      "Consider promotional listing"
    ]
  }
}
```

### Sanitize Vehicle Data

Sanitizes and standardizes vehicle information.

```
POST /vehicle-data/sanitize
```

**Request Body**:

```json
{
  "make": "  toyota ",
  "model": "camrY",
  "color": "SILVER metallic"
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "make": "Toyota",
    "model": "Camry",
    "color": "Silver Metallic",
    "make_id": 1,
    "model_id": 1,
    "color_id": 3
  }
}
```

### Data Validation

Validates data according to application rules.

```
POST /validate
```

**Request Body**:

```json
{
  "validate_type": "vehicle",
  "data": {
    "vehicle_name": "2019 Honda Accord",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "year": 2019,
    "colour": "Silver",
    "purchase_price": 16500.00
  }
}
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  }
}
```

Or with validation errors:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "is_valid": false,
      "errors": [
        {
          "field": "year",
          "message": "Year cannot be in the future"
        },
        {
          "field": "purchase_price",
          "message": "Purchase price must be a positive number"
        }
      ],
      "warnings": [
        {
          "field": "vehicle_make",
          "message": "Uncommon vehicle make, please verify"
        }
      ]
    }
  }
}
``` 