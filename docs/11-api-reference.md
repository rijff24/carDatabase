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
  "vehicle_name": "2020 Honda Accord",
  "vehicle_make": "Honda",
  "vehicle_model": "Accord",
  "vehicle_year": 2020,
  "purchase_price": 18000.00,
  "date_bought": "2023-03-01",
  "refuel_cost": 45.00,
  "dealer_id": 3
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "car_id": 126,
    "vehicle_name": "2020 Honda Accord",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "vehicle_year": 2020,
    "purchase_price": 18000.00,
    "date_bought": "2023-03-01",
    "repair_status": "Waiting for Repairs",
    "refuel_cost": 45.00,
    "dealer_id": 3,
    "links": {
      "self": "/api/v1/vehicles/126"
    }
  }
}
```

### Update Vehicle

Updates a vehicle record.

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
  "purchase_price": 17500.00,
  "refuel_cost": 50.00,
  "repair_status": "Ready for Display"
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "car_id": 126,
    "vehicle_name": "2020 Honda Accord",
    "vehicle_make": "Honda",
    "vehicle_model": "Accord",
    "vehicle_year": 2020,
    "purchase_price": 17500.00,
    "date_bought": "2023-03-01",
    "repair_status": "Ready for Display",
    "refuel_cost": 50.00,
    "dealer_id": 3,
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

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "message": "Vehicle with ID 126 deleted successfully"
  }
}
```

## Repairs API

### Get Repairs for Vehicle

Retrieves all repairs for a specific vehicle.

```
GET /vehicles/{car_id}/repairs
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| car_id    | int  | ID of the vehicle  |

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "repair_id": 5,
      "car_id": 1,
      "description": "Oil change and inspection",
      "provider_id": 2,
      "provider_name": "QuickService Auto",
      "start_date": "2023-01-16",
      "end_date": "2023-01-16",
      "repair_cost": 95.00,
      "parts_cost": 30.00,
      "labor_cost": 65.00,
      "duration_days": 1,
      "links": {
        "self": "/api/v1/repairs/5",
        "vehicle": "/api/v1/vehicles/1",
        "provider": "/api/v1/providers/2"
      }
    }
    // Additional repairs...
  ],
  "meta": {
    "total": 1,
    "total_cost": 95.00
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
  "description": "Pre-sale inspection and detailing",
  "provider_id": 3,
  "start_date": "2023-03-05",
  "estimated_cost": 250.00
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "repair_id": 203,
    "car_id": 126,
    "description": "Pre-sale inspection and detailing",
    "provider_id": 3,
    "provider_name": "Premium Auto Detail",
    "start_date": "2023-03-05",
    "repair_cost": 0.00,
    "parts_cost": 0.00,
    "labor_cost": 0.00,
    "links": {
      "self": "/api/v1/repairs/203",
      "vehicle": "/api/v1/vehicles/126",
      "provider": "/api/v1/providers/3"
    }
  }
}
```

### Complete Repair

Marks a repair as complete.

```
PUT /repairs/{repair_id}/complete
```

**Path Parameters**:

| Parameter | Type | Description        |
|-----------|------|--------------------|
| repair_id | int  | ID of the repair   |

**Request Body**:

```json
{
  "end_date": "2023-03-07",
  "repair_cost": 275.00,
  "parts_cost": 50.00,
  "labor_cost": 225.00,
  "notes": "Completed detailing work and full inspection."
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "repair_id": 203,
    "car_id": 126,
    "description": "Pre-sale inspection and detailing",
    "provider_id": 3,
    "provider_name": "Premium Auto Detail",
    "start_date": "2023-03-05",
    "end_date": "2023-03-07",
    "repair_cost": 275.00,
    "parts_cost": 50.00,
    "labor_cost": 225.00,
    "duration_days": 2,
    "notes": "Completed detailing work and full inspection.",
    "links": {
      "self": "/api/v1/repairs/203",
      "vehicle": "/api/v1/vehicles/126",
      "provider": "/api/v1/providers/3"
    }
  }
}
```

## Sales API

### Record Sale

Records a vehicle sale.

```
POST /sales
```

**Request Body**:

```json
{
  "car_id": 126,
  "dealer_id": 5,
  "sale_price": 22500.00,
  "sale_date": "2023-03-15",
  "payment_method": "Finance",
  "customer_name": "John Smith",
  "customer_contact": "john.smith@example.com"
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "sale_id": 87,
    "car_id": 126,
    "dealer_id": 5,
    "dealer_name": "Sarah Johnson",
    "sale_price": 22500.00,
    "sale_date": "2023-03-15",
    "payment_method": "Finance",
    "customer_name": "John Smith",
    "customer_contact": "john.smith@example.com",
    "profit": 4675.00,
    "profit_margin": 20.78,
    "commission": 5000.00,
    "links": {
      "self": "/api/v1/sales/87",
      "vehicle": "/api/v1/vehicles/126",
      "dealer": "/api/v1/dealers/5"
    }
  }
}
```

### Get Sales List

Retrieves a list of sales.

```
GET /sales
```

**Query Parameters**:

| Parameter    | Type      | Description                       |
|--------------|-----------|-----------------------------------|
| start_date   | date      | Filter by start date              |
| end_date     | date      | Filter by end date                |
| dealer_id    | int       | Filter by dealer                  |
| limit        | int       | Maximum number of results         |
| offset       | int       | Offset for pagination             |

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "sale_id": 87,
      "car_id": 126,
      "vehicle_name": "2020 Honda Accord",
      "dealer_id": 5,
      "dealer_name": "Sarah Johnson",
      "sale_price": 22500.00,
      "sale_date": "2023-03-15",
      "profit": 4675.00,
      "profit_margin": 20.78,
      "commission": 5000.00,
      "links": {
        "self": "/api/v1/sales/87",
        "vehicle": "/api/v1/vehicles/126",
        "dealer": "/api/v1/dealers/5"
      }
    }
    // Additional sales...
  ],
  "meta": {
    "total": 87,
    "limit": 20,
    "offset": 0,
    "total_revenue": 1659750.00,
    "total_profit": 342500.00,
    "avg_profit_margin": 21.35,
    "next": "/api/v1/sales?limit=20&offset=20",
    "previous": null
  }
}
```

## Dealers API

### Get Dealers List

Retrieves a list of dealers.

```
GET /dealers
```

**Example Response**:

```json
{
  "status": "success",
  "data": [
    {
      "dealer_id": 1,
      "name": "Michael Brown",
      "contact_name": "Michael Brown",
      "contact_email": "michael.brown@example.com",
      "contact_phone": "555-123-4567",
      "commission_rate": 10.00,
      "active": true,
      "links": {
        "self": "/api/v1/dealers/1",
        "sales": "/api/v1/dealers/1/sales"
      }
    }
    // Additional dealers...
  ],
  "meta": {
    "total": 8
  }
}
```

### Get Dealer Performance

Retrieves performance metrics for a dealer.

```
GET /dealers/{dealer_id}/performance
```

**Path Parameters**:

| Parameter  | Type | Description        |
|------------|------|--------------------|
| dealer_id  | int  | ID of the dealer   |

**Query Parameters**:

| Parameter  | Type      | Description                       |
|------------|-----------|-----------------------------------|
| start_date | date      | Filter by start date              |
| end_date   | date      | Filter by end date                |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "dealer_id": 5,
    "name": "Sarah Johnson",
    "metrics": {
      "total_sales": 15,
      "total_revenue": 337500.00,
      "total_profit": 67450.00,
      "avg_profit_per_sale": 4496.67,
      "avg_profit_margin": 19.85,
      "total_commission": 75000.00,
      "avg_days_to_sell": 18.3
    },
    "monthly_performance": [
      {
        "month": "2023-01",
        "sales_count": 3,
        "revenue": 67500.00,
        "profit": 13280.00,
        "avg_margin": 19.45
      },
      // Additional months...
    ],
    "links": {
      "self": "/api/v1/dealers/5",
      "sales": "/api/v1/dealers/5/sales"
    }
  }
}
```

## Reports API

### Generate Financial Report

Generates a financial report.

```
GET /reports/financial
```

**Query Parameters**:

| Parameter  | Type      | Description                       |
|------------|-----------|-----------------------------------|
| start_date | date      | Filter by start date              |
| end_date   | date      | Filter by end date                |
| type       | string    | Report type (profit, revenue)     |
| format     | string    | Response format (json, csv, pdf)  |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "report_type": "financial",
    "period": {
      "start_date": "2023-01-01",
      "end_date": "2023-03-31"
    },
    "summary": {
      "total_revenue": 547250.00,
      "total_costs": 428930.00,
      "total_profit": 118320.00,
      "profit_margin": 21.62,
      "total_commission": 125000.00
    },
    "monthly_breakdown": [
      {
        "month": "2023-01",
        "revenue": 183750.00,
        "costs": 145650.00,
        "profit": 38100.00,
        "margin": 20.73
      },
      // Additional months...
    ],
    "links": {
      "self": "/api/v1/reports/financial?start_date=2023-01-01&end_date=2023-03-31",
      "csv": "/api/v1/reports/financial?start_date=2023-01-01&end_date=2023-03-31&format=csv",
      "pdf": "/api/v1/reports/financial?start_date=2023-01-01&end_date=2023-03-31&format=pdf"
    }
  }
}
```

### Generate Inventory Report

Generates an inventory report.

```
GET /reports/inventory
```

**Query Parameters**:

| Parameter  | Type      | Description                       |
|------------|-----------|-----------------------------------|
| status     | string    | Filter by vehicle status          |
| format     | string    | Response format (json, csv, pdf)  |

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "report_type": "inventory",
    "generated_at": "2023-04-01T12:00:00Z",
    "summary": {
      "total_vehicles": 42,
      "total_investment": 672450.00,
      "average_days_in_inventory": 18.5
    },
    "status_breakdown": {
      "Waiting for Repairs": 8,
      "In Repair": 5,
      "Ready for Display": 7,
      "On Display": 22,
      "Sold": 0
    },
    "location_breakdown": {
      "Main Showroom": 15,
      "North Lot": 7,
      "Service Center": 13,
      "Unassigned": 7
    },
    "aging_breakdown": {
      "0-30 days": 25,
      "31-60 days": 12,
      "61-90 days": 3,
      "91+ days": 2
    },
    "links": {
      "self": "/api/v1/reports/inventory",
      "csv": "/api/v1/reports/inventory?format=csv",
      "pdf": "/api/v1/reports/inventory?format=pdf"
    }
  }
}
```

## Error Codes

| Code            | Description                                       |
|-----------------|---------------------------------------------------|
| UNAUTHORIZED    | Authentication required or failed                 |
| FORBIDDEN       | User doesn't have permission                      |
| NOT_FOUND       | Resource not found                                |
| VALIDATION      | Validation error in input data                    |
| BUSINESS_RULE   | Operation violates a business rule                |
| CONFLICT        | Resource conflict (e.g., duplicate data)          |
| SERVER_ERROR    | Internal server error                             |
| SERVICE_DOWN    | External service dependency unavailable           |
| RATE_LIMIT      | API rate limit exceeded                           |

## Rate Limiting

The API implements rate limiting to ensure stability:

- Standard users: 100 requests per minute
- Premium users: 300 requests per minute

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1617278400
```

## Webhooks

The application can send webhook notifications for various events:

### Webhook Registration

```
POST /webhooks
```

**Request Body**:

```json
{
  "url": "https://your-app.com/webhook-receiver",
  "events": ["vehicle.created", "sale.recorded", "repair.completed"],
  "secret": "your_webhook_secret"
}
```

**Example Response**:

```json
{
  "status": "success",
  "data": {
    "webhook_id": 12,
    "url": "https://your-app.com/webhook-receiver",
    "events": ["vehicle.created", "sale.recorded", "repair.completed"],
    "created_at": "2023-04-01T12:00:00Z",
    "status": "active"
  }
}
```

### Webhook Payload Example

```json
{
  "event": "sale.recorded",
  "timestamp": "2023-03-15T14:35:22Z",
  "webhook_id": 12,
  "data": {
    "sale_id": 87,
    "car_id": 126,
    "vehicle_name": "2020 Honda Accord",
    "dealer_id": 5,
    "dealer_name": "Sarah Johnson",
    "sale_price": 22500.00,
    "sale_date": "2023-03-15",
    "profit": 4675.00
  }
}
```

### Available Events

| Event Name         | Description                                   |
|--------------------|-----------------------------------------------|
| vehicle.created    | New vehicle added to inventory                |
| vehicle.updated    | Vehicle information updated                   |
| vehicle.status     | Vehicle status changed                        |
| repair.created     | New repair record created                     |
| repair.completed   | Repair marked as complete                     |
| sale.recorded      | Vehicle sale recorded                         |
| report.generated   | Report generation completed                   |

## API Versioning

The API implements versioning to ensure backward compatibility:

- Current version: v1
- Versions are specified in the URL path: `/api/v1/...`
- Version-specific documentation is available at: `/api/docs/v1`

## Deprecation Policy

When API features are deprecated:

1. Deprecation warnings are included in response headers:
   ```
   X-API-Warning: The 'dealer_code' field is deprecated and will be removed in v2
   ```

2. Deprecated features remain available for at least 6 months

3. Migration guides are published in the developer documentation

## SDK Libraries

Official client libraries are available for:

- Python: `pip install car-tracking-api-client`
- JavaScript: `npm install car-tracking-api-client`
- PHP: `composer require car-tracking/api-client`

Example usage (Python):

```python
from car_tracking_api import CarTrackingAPI

api = CarTrackingAPI('your_api_key')

# Get list of vehicles
vehicles = api.vehicles.list(status='On Display')

# Record a sale
sale = api.sales.create(
    car_id=126,
    dealer_id=5,
    sale_price=22500.00,
    sale_date='2023-03-15'
) 