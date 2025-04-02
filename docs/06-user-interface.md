# User Interface

This document details the user interface components, screens, forms, and navigation flow of the Car Repair and Sales Tracking Application.

## UI Framework

The application uses the following UI technologies:
- **Jinja2**: Server-side templating engine for rendering HTML
- **Bootstrap 4**: CSS framework for responsive design
- **jQuery**: JavaScript library for DOM manipulation
- **Chart.js**: JavaScript library for data visualization
- **Font Awesome**: Icon library for visual elements

## Navigation Structure

The application has a consistent navigation structure throughout:

```
├── Primary Navigation (Top Navbar)
│   ├── Dashboard
│   ├── Inventory
│   ├── Repairs
│   ├── Sales
│   ├── Reports
│   ├── Admin
│   └── User Menu
├── Secondary Navigation (Sidebar or Tab Bars)
│   └── Context-specific navigation based on primary selection
└── Content Area
    └── Main content for the selected view
```

### Main Navigation Items

1. **Dashboard**: Overview of key metrics and recent activity
2. **Inventory**: Vehicle management and stand allocation
3. **Repairs**: Repair tracking and management
4. **Sales**: Sales recording and dealer performance
5. **Reports**: Financial and operational reporting
6. **Admin**: System configuration and user management
7. **User Menu**: Profile, preferences, and logout

## Key Screens

### 1. Dashboard

![Dashboard](../app/static/img/docs/dashboard.png)

The dashboard provides an at-a-glance view of the business status:

- **Key Performance Indicators**:
  - Cars in inventory
  - Cars sold this month
  - Average profit margin
  - Total profit this month

- **Recent Activity**:
  - Latest sales
  - Recently added vehicles
  - Vehicles ready for display

- **Charts and Graphs**:
  - Monthly sales trend
  - Profit margin by vehicle type
  - Repair time distribution

### 2. Inventory Management

#### 2.1 Vehicle List

![Vehicle List](../app/static/img/docs/vehicle_list.png)

- **Features**:
  - Filterable list of all vehicles
  - Status indicators (color-coded)
  - Quick action buttons
  - Search functionality
  
- **Columns**:
  - Vehicle ID
  - Make/Model
  - Status
  - Purchase Date
  - Purchase Price
  - Current Location
  - Actions

#### 2.2 Vehicle Detail

![Vehicle Detail](../app/static/img/docs/vehicle_detail.png)

- **Features**:
  - Comprehensive vehicle information
  - Status history
  - Financial summary
  - Repair history
  
- **Sections**:
  - Basic Information
  - Financial Details
  - Location History
  - Repair Records
  - Sales Details (if sold)

#### 2.3 Stand Management

![Stand Management](../app/static/img/docs/stand_management.png)

- **Features**:
  - Visual representation of stands
  - Capacity indicators
  - Drag-and-drop vehicle assignment
  
- **Elements**:
  - Stand cards with capacity bars
  - Vehicle thumbnails
  - Add/Edit stand buttons
  - Filter and search options

### 3. Repair Management

#### 3.1 Repair List

![Repair List](../app/static/img/docs/repair_list.png)

- **Features**:
  - List of all repairs with status
  - Filterable by status and date range
  - Sort options
  
- **Columns**:
  - Repair ID
  - Vehicle
  - Provider
  - Start Date
  - End Date (if completed)
  - Status
  - Cost
  - Actions

#### 3.2 Repair Detail

![Repair Detail](../app/static/img/docs/repair_detail.png)

- **Features**:
  - Detailed repair information
  - Parts list with costs
  - Status update controls
  
- **Sections**:
  - Basic Information
  - Vehicle Details
  - Repair Provider
  - Parts Used
  - Status Timeline
  - Cost Summary

#### 3.3 Parts Management

![Parts Management](../app/static/img/docs/parts_management.png)

- **Features**:
  - Inventory of parts
  - Usage tracking
  - Add/Edit part controls
  
- **Elements**:
  - Parts list with search
  - Stock level indicators
  - Cost history
  - Usage reports

### 4. Sales Management

#### 4.1 Sales List

![Sales List](../app/static/img/docs/sales_list.png)

- **Features**:
  - List of all sales
  - Filterable by date range and dealer
  - Financial summaries
  
- **Columns**:
  - Sale ID
  - Vehicle
  - Sale Date
  - Dealer
  - Sale Price
  - Profit
  - Commission
  - Actions

#### 4.2 Sale Detail

![Sale Detail](../app/static/img/docs/sale_detail.png)

- **Features**:
  - Complete sale information
  - Financial breakdown
  - Related documents
  
- **Sections**:
  - Sale Information
  - Vehicle Details
  - Dealer Information
  - Financial Summary
  - Payment Details
  - Customer Information

#### 4.3 Dealer Performance

![Dealer Performance](../app/static/img/docs/dealer_performance.png)

- **Features**:
  - Dealer sales performance metrics
  - Commission totals
  - Performance comparisons
  
- **Elements**:
  - Dealer list
  - Performance charts
  - Sales history
  - Commission calculations

### 5. Reporting

#### 5.1 Financial Reports

![Financial Reports](../app/static/img/docs/financial_reports.png)

- **Features**:
  - Profit and loss statements
  - Revenue breakdowns
  - Expense tracking
  
- **Report Types**:
  - Monthly Profit Summary
  - Vehicle Profitability Analysis
  - Commission Payments
  - Investment Returns

#### 5.2 Operational Reports

![Operational Reports](../app/static/img/docs/operational_reports.png)

- **Features**:
  - Inventory status
  - Repair efficiency
  - Sales velocity
  
- **Report Types**:
  - Inventory Aging
  - Repair Duration Analysis
  - Stand Utilization
  - Vehicle Turnover Rate

#### 5.3 Custom Reports

![Custom Reports](../app/static/img/docs/custom_reports.png)

- **Features**:
  - Build custom reports
  - Save report templates
  - Export options (CSV, PDF)
  
- **Elements**:
  - Field selector
  - Filter builder
  - Visualization options
  - Scheduling controls

### 6. Administration

#### 6.1 System Settings

![System Settings](../app/static/img/docs/system_settings.png)

The System Settings page provides a centralized interface for controlling application behavior and preferences. It is accessible only to users with the admin role.

- **Features**:
  - Tabbed interface for organizing different setting categories
  - Real-time validation of input values
  - Role-based access control
  - Immediate application of settings
  
- **Tabs**:
  
  1. **General Configuration**
     - Interface preferences
     - Dark mode toggle
     - UI behavior settings
     
  2. **Thresholds & Rules**
     - Numerical thresholds for business rules
     - Feature toggles for enabling/disabling functionality
     - Warning and alert thresholds
     
  3. **User Management**
     - User listing with role information
     - Interface for creating new users
     - Edit existing user information
     - Reset user passwords
     - Delete users
     
- **Setting Types**:
  - Boolean toggles (on/off switches)
  - Numeric inputs with validation
  - Text fields with validation
  - Dropdown selectors
  
- **Implementation**:
  - Server-side validation ensures valid settings
  - Changes take effect immediately
  - Settings are stored in the database
  - Centralized access via `Setting.get_setting()` method

#### 6.2 User Management

![User Management](../app/static/img/docs/user_management.png)

- **Features**:
  - User account management
  - Role assignment
  - Access control
  
- **Elements**:
  - User list
  - Role editor
  - Permission matrix
  - Activity logs

#### 6.3 System Configuration

![System Configuration](../app/static/img/docs/system_configuration.png)

- **Features**:
  - Application settings
  - Business rules configuration
  - Integration settings
  
- **Settings Categories**:
  - General Settings
  - Financial Parameters
  - Repair Provider Management
  - Stand Configuration
  - Backup and Restore

## Form Controls

### Standard Form Elements

The application uses consistent form elements throughout:

1. **Text Input**:
   ```html
   <div class="form-group">
     <label for="vehicleName">Vehicle Name</label>
     <input type="text" class="form-control" id="vehicleName" name="vehicle_name" required>
     <small class="form-text text-muted">Enter the complete vehicle name including year, make, and model</small>
   </div>
   ```

2. **Date Picker**:
   ```html
   <div class="form-group">
     <label for="purchaseDate">Purchase Date</label>
     <input type="date" class="form-control datepicker" id="purchaseDate" name="purchase_date" required>
   </div>
   ```

3. **Selection Dropdown**:
   ```html
   <div class="form-group">
     <label for="repairProvider">Repair Provider</label>
     <select class="form-control" id="repairProvider" name="provider_id">
       <option value="">Select Provider...</option>
       {% for provider in providers %}
         <option value="{{ provider.provider_id }}">{{ provider.name }}</option>
       {% endfor %}
     </select>
   </div>
   ```

4. **Numeric Input**:
   ```html
   <div class="form-group">
     <label for="purchasePrice">Purchase Price</label>
     <div class="input-group">
       <div class="input-group-prepend">
         <span class="input-group-text">$</span>
       </div>
       <input type="number" class="form-control" id="purchasePrice" name="purchase_price" min="0" step="0.01" required>
     </div>
   </div>
   ```

5. **Status Selection**:
   ```html
   <div class="form-group">
     <label>Repair Status</label>
     <div class="btn-group btn-group-toggle w-100" data-toggle="buttons">
       {% for status in valid_statuses %}
         <label class="btn btn-outline-primary {% if car.repair_status == status %}active{% endif %}">
           <input type="radio" name="repair_status" value="{{ status }}" {% if car.repair_status == status %}checked{% endif %}>
           {{ status }}
         </label>
       {% endfor %}
     </div>
   </div>
   ```

### Form Validation

The application implements both client-side and server-side validation:

1. **Client-Side Validation**:
   ```javascript
   $(document).ready(function() {
     $('#vehicleForm').validate({
       rules: {
         vehicle_name: {
           required: true,
           minlength: 3
         },
         purchase_price: {
           required: true,
           number: true,
           min: 0
         },
         purchase_date: {
           required: true,
           date: true
         }
       },
       messages: {
         vehicle_name: {
           required: "Please enter the vehicle name",
           minlength: "Vehicle name must be at least 3 characters"
         },
         purchase_price: {
           required: "Please enter the purchase price",
           number: "Please enter a valid number",
           min: "Price cannot be negative"
         },
         purchase_date: {
           required: "Please enter the purchase date",
           date: "Please enter a valid date"
         }
       },
       errorElement: 'div',
       errorClass: 'invalid-feedback',
       highlight: function(element) {
         $(element).addClass('is-invalid');
       },
       unhighlight: function(element) {
         $(element).removeClass('is-invalid');
       },
       errorPlacement: function(error, element) {
         error.insertAfter(element);
       }
     });
   });
   ```

2. **Server-Side Validation**:
   ```python
   def validate_vehicle_form(form_data):
       errors = {}
       
       # Validate vehicle name
       if not form_data.get('vehicle_name'):
           errors['vehicle_name'] = 'Vehicle name is required'
       
       # Validate purchase price
       try:
           price = float(form_data.get('purchase_price', 0))
           if price < 0:
               errors['purchase_price'] = 'Price cannot be negative'
       except ValueError:
           errors['purchase_price'] = 'Invalid price format'
       
       # Validate purchase date
       try:
           purchase_date = datetime.strptime(form_data.get('purchase_date', ''), '%Y-%m-%d').date()
           if purchase_date > datetime.now().date():
               errors['purchase_date'] = 'Purchase date cannot be in the future'
       except ValueError:
           errors['purchase_date'] = 'Invalid date format'
       
       return errors
   ```

## UI Components

### Data Tables

Data tables are used throughout the application for displaying tabular data:

```html
<table class="table table-striped table-hover" id="vehicleTable">
  <thead>
    <tr>
      <th>ID</th>
      <th>Vehicle</th>
      <th>Status</th>
      <th>Purchase Date</th>
      <th>Purchase Price</th>
      <th>Location</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for car in cars %}
    <tr class="status-{{ car.repair_status|slugify }}">
      <td>{{ car.car_id }}</td>
      <td>{{ car.vehicle_name }}</td>
      <td><span class="badge badge-{{ status_colors[car.repair_status] }}">{{ car.repair_status }}</span></td>
      <td>{{ car.date_bought|date }}</td>
      <td>${{ car.purchase_price|floatformat:2 }}</td>
      <td>{{ car.current_location }}</td>
      <td>
        <div class="btn-group btn-group-sm">
          <a href="{{ url_for('inventory.view_car', car_id=car.car_id) }}" class="btn btn-info">
            <i class="fas fa-eye"></i>
          </a>
          <a href="{{ url_for('inventory.edit_car', car_id=car.car_id) }}" class="btn btn-primary">
            <i class="fas fa-edit"></i>
          </a>
          <!-- Additional action buttons -->
        </div>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<script>
  $(document).ready(function() {
    $('#vehicleTable').DataTable({
      "order": [[0, "desc"]],
      "pageLength": 25,
      "responsive": true
    });
  });
</script>
```

### Modal Dialogs

Modal dialogs are used for quick actions without navigating away from the current page:

```html
<!-- Delete Confirmation Modal -->
<div class="modal fade" id="deleteModal" tabindex="-1" role="dialog" aria-labelledby="deleteModalLabel" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header bg-danger text-white">
        <h5 class="modal-title" id="deleteModalLabel">Confirm Deletion</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        Are you sure you want to delete this vehicle? This action cannot be undone.
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
        <form id="deleteForm" method="POST" action="">
          <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
          <button type="submit" class="btn btn-danger">Delete</button>
        </form>
      </div>
    </div>
  </div>
</div>

<script>
  // Update delete form action when modal is opened
  $('#deleteModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var carId = button.data('car-id');
    var carName = button.data('car-name');
    
    var modal = $(this);
    modal.find('.modal-body').text('Are you sure you want to delete ' + carName + '? This action cannot be undone.');
    modal.find('#deleteForm').attr('action', '/inventory/delete/' + carId);
  });
</script>
```

### Charts and Graphs

Data visualization is implemented using Chart.js:

```html
<div class="card">
  <div class="card-header">
    Monthly Sales Performance
  </div>
  <div class="card-body">
    <canvas id="salesChart" width="400" height="200"></canvas>
  </div>
</div>

<script>
  $(document).ready(function() {
    var ctx = document.getElementById('salesChart').getContext('2d');
    var salesChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: {{ months|safe }},
        datasets: [{
          label: 'Number of Sales',
          data: {{ sales_counts|safe }},
          backgroundColor: 'rgba(54, 162, 235, 0.5)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }, {
          label: 'Profit Margin (%)',
          data: {{ profit_margins|safe }},
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1,
          type: 'line',
          yAxisID: 'y-axis-2'
        }]
      },
      options: {
        responsive: true,
        scales: {
          yAxes: [{
            id: 'y-axis-1',
            type: 'linear',
            position: 'left',
            ticks: {
              beginAtZero: true
            },
            scaleLabel: {
              display: true,
              labelString: 'Number of Sales'
            }
          }, {
            id: 'y-axis-2',
            type: 'linear',
            position: 'right',
            ticks: {
              beginAtZero: true,
              callback: function(value) {
                return value + '%';
              }
            },
            scaleLabel: {
              display: true,
              labelString: 'Profit Margin (%)'
            },
            gridLines: {
              drawOnChartArea: false
            }
          }]
        }
      }
    });
  });
</script>
```

## Responsive Design

The application is fully responsive, adapting to different screen sizes:

1. **Desktop Layout**:
   - Full navigation visible
   - Multi-column layouts
   - Detailed data tables
   - Advanced filtering options

2. **Tablet Layout**:
   - Condensed navigation
   - Reduced column layouts
   - Scrollable tables
   - Simplified filters

3. **Mobile Layout**:
   - Hamburger menu for navigation
   - Single column layouts
   - Card-based data presentation
   - Essential filtering only

Example of responsive design implementation:

```html
<div class="row">
  <!-- Vehicle Details Column -->
  <div class="col-lg-8 col-md-6 col-sm-12">
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="card-title">Vehicle Details</h5>
      </div>
      <div class="card-body">
        <!-- Vehicle information -->
      </div>
    </div>
  </div>
  
  <!-- Financial Summary Column -->
  <div class="col-lg-4 col-md-6 col-sm-12">
    <div class="card mb-4">
      <div class="card-header">
        <h5 class="card-title">Financial Summary</h5>
      </div>
      <div class="card-body">
        <!-- Financial information -->
      </div>
    </div>
  </div>
</div>

<!-- Responsive utility classes for visibility -->
<div class="d-none d-md-block">
  <!-- This content only shows on medium screens and larger -->
  <div class="advanced-filters">
    <!-- Advanced filtering options -->
  </div>
</div>

<div class="d-block d-md-none">
  <!-- This content only shows on small screens -->
  <button class="btn btn-primary btn-block" data-toggle="collapse" data-target="#mobileFilters">
    Show Filters
  </button>
  <div id="mobileFilters" class="collapse">
    <!-- Simplified filtering options -->
  </div>
</div>
```

## Accessibility Features

The application implements several accessibility features:

1. **Semantic HTML**:
   ```html
   <main role="main">
     <section aria-labelledby="pageTitle">
       <h1 id="pageTitle">Inventory Management</h1>
       <!-- Content -->
     </section>
   </main>
   ```

2. **ARIA Attributes**:
   ```html
   <div id="inventoryTab" role="tabpanel" aria-labelledby="inventory-tab">
     <!-- Tab content -->
   </div>
   ```

3. **Keyboard Navigation**:
   ```javascript
   $('.nav-item').keydown(function(e) {
     // Handle arrow key navigation
     if (e.keyCode === 39) { // Right arrow
       $(this).next().find('a').focus();
     } else if (e.keyCode === 37) { // Left arrow
       $(this).prev().find('a').focus();
     }
   });
   ```

4. **Screen Reader Support**:
   ```html
   <button class="btn btn-primary" aria-label="Add new vehicle">
     <i class="fas fa-plus" aria-hidden="true"></i>
   </button>
   ```

5. **Color Contrast**:
   ```css
   .status-badge {
     color: #fff;
     background-color: #007bff; /* WCAG AA compliant contrast */
     padding: 0.25rem 0.5rem;
     border-radius: 0.25rem;
   }
   ```

## UI Workflows

### Adding a New Vehicle

1. User navigates to Inventory → Add Vehicle
2. Form is presented with required fields:
   - Vehicle information
   - Purchase details
   - Initial status
3. User completes form and submits
4. System validates input
5. On success, redirect to vehicle detail page
6. On error, form is redisplayed with validation messages

### Recording a Vehicle Sale

1. User navigates to vehicle detail page
2. User clicks "Record Sale" button
3. Sale form modal appears with fields:
   - Sale price
   - Sale date
   - Dealer
   - Payment method
4. User completes form and submits
5. System validates input
6. System calculates profit and commission
7. On success, vehicle status updates to "Sold"
8. Sales record is created
9. User is redirected to sale detail page

### Managing Repairs

1. User navigates to Repairs → Add Repair
2. User selects vehicle from dropdown
3. User enters repair details:
   - Description
   - Provider
   - Start date
   - Estimated cost
4. User adds parts to repair (optional)
5. System creates repair record
6. As repair progresses, user updates status
7. When complete, user marks as finished and enters actual cost
8. System updates vehicle repair history and total repair cost

## Custom UI Elements

### Status Timeline

The application implements a custom status timeline to visualize the progression of vehicles through the workflow:

```html
<div class="status-timeline">
  <div class="timeline-item {{ 'active' if car.repair_status == 'Waiting for Repairs' else 'complete' if car_timeline_position > 0 else '' }}">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <h3 class="timeline-title">Waiting for Repairs</h3>
      <p>{{ car.date_bought|date }}</p>
    </div>
  </div>
  
  <div class="timeline-item {{ 'active' if car.repair_status == 'In Repair' else 'complete' if car_timeline_position > 1 else '' }}">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <h3 class="timeline-title">In Repair</h3>
      <p>{{ car.date_repair_started|date if car.date_repair_started else 'Not started' }}</p>
    </div>
  </div>
  
  <div class="timeline-item {{ 'active' if car.repair_status == 'Ready for Display' else 'complete' if car_timeline_position > 2 else '' }}">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <h3 class="timeline-title">Ready for Display</h3>
      <p>{{ car.date_repair_completed|date if car.date_repair_completed else 'Not completed' }}</p>
    </div>
  </div>
  
  <div class="timeline-item {{ 'active' if car.repair_status == 'On Display' else 'complete' if car_timeline_position > 3 else '' }}">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <h3 class="timeline-title">On Display</h3>
      <p>{{ car.date_added_to_stand|date if car.date_added_to_stand else 'Not on display' }}</p>
    </div>
  </div>
  
  <div class="timeline-item {{ 'active' if car.repair_status == 'Sold' else '' }}">
    <div class="timeline-marker"></div>
    <div class="timeline-content">
      <h3 class="timeline-title">Sold</h3>
      <p>{{ car.date_sold|date if car.date_sold else 'Not sold' }}</p>
    </div>
  </div>
</div>
```

### Financial Card

The application uses a custom financial card component to display financial summaries:

```html
<div class="financial-card">
  <div class="financial-card-header">
    <h3>Financial Summary</h3>
  </div>
  <div class="financial-card-body">
    <div class="financial-item">
      <div class="financial-label">Purchase Price</div>
      <div class="financial-value">${{ car.purchase_price|floatformat:2 }}</div>
    </div>
    <div class="financial-item">
      <div class="financial-label">Repair Cost</div>
      <div class="financial-value">${{ car.total_repair_cost|floatformat:2 }}</div>
    </div>
    <div class="financial-item">
      <div class="financial-label">Refuel Cost</div>
      <div class="financial-value">${{ car.refuel_cost|floatformat:2 }}</div>
    </div>
    <div class="financial-item total">
      <div class="financial-label">Total Investment</div>
      <div class="financial-value">${{ car.total_investment|floatformat:2 }}</div>
    </div>
    {% if car.sale_price %}
    <div class="financial-item">
      <div class="financial-label">Sale Price</div>
      <div class="financial-value">${{ car.sale_price|floatformat:2 }}</div>
    </div>
    <div class="financial-item profit {{ 'positive' if car.profit > 0 else 'negative' }}">
      <div class="financial-label">Profit</div>
      <div class="financial-value">${{ car.profit|floatformat:2 }}</div>
    </div>
    <div class="financial-item">
      <div class="financial-label">Profit Margin</div>
      <div class="financial-value">{{ car.profit_margin|floatformat:1 }}%</div>
    </div>
    {% endif %}
  </div>
</div>
```

## UI Error Handling

The application implements consistent error handling throughout the UI:

1. **Form Validation Errors**:
   ```html
   {% if form.errors %}
   <div class="alert alert-danger">
     <h4 class="alert-heading">There were errors with your submission</h4>
     <ul>
       {% for field, errors in form.errors.items() %}
         {% for error in errors %}
           <li>{{ field }}: {{ error }}</li>
         {% endfor %}
       {% endfor %}
     </ul>
   </div>
   {% endif %}
   ```

2. **Flash Messages**:
   ```html
   {% with messages = get_flashed_messages(with_categories=true) %}
     {% if messages %}
       {% for category, message in messages %}
         <div class="alert alert-{{ category }} alert-dismissible fade show">
           {{ message }}
           <button type="button" class="close" data-dismiss="alert" aria-label="Close">
             <span aria-hidden="true">&times;</span>
           </button>
         </div>
       {% endfor %}
     {% endif %}
   {% endwith %}
   ```

3. **AJAX Error Handling**:
   ```javascript
   $.ajax({
     url: '/api/vehicle/' + carId,
     type: 'GET',
     dataType: 'json',
     success: function(data) {
       // Handle successful response
       updateVehicleDetails(data);
     },
     error: function(xhr, status, error) {
       // Handle error
       let errorMessage;
       try {
         const response = JSON.parse(xhr.responseText);
         errorMessage = response.error || 'An unknown error occurred';
       } catch (e) {
         errorMessage = 'Could not process the server response';
       }
       
       // Display error message
       showErrorToast(errorMessage);
       
       // Log for debugging
       console.error('API Error:', errorMessage);
     }
   });
   ```

4. **Empty State Handling**:
   ```html
   {% if not cars %}
   <div class="empty-state">
     <div class="empty-state-icon">
       <i class="fas fa-car fa-4x"></i>
     </div>
     <h3>No Vehicles Found</h3>
     <p>There are no vehicles matching your search criteria.</p>
     <a href="{{ url_for('inventory.add_car') }}" class="btn btn-primary">
       <i class="fas fa-plus"></i> Add Vehicle
     </a>
   </div>
   {% else %}
   <!-- Vehicle list -->
   {% endif %}
   ``` 