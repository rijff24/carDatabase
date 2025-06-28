# User Interface

This document details the user interface components, screens, forms, and navigation flow of the Car Repair and Sales Tracking Application.

## UI Framework

The application uses the following UI technologies:
- **Jinja2**: Server-side templating engine for rendering HTML
- **Bootstrap 5**: CSS framework for responsive design
- **jQuery**: JavaScript library for DOM manipulation
- **Chart.js**: JavaScript library for data visualization
- **Font Awesome**: Icon library for visual elements

### Mobile-First Responsive Design

The application implements a comprehensive mobile-first responsive design approach:

#### Responsive Breakpoints
- **Small Mobile**: ≤576px (Primary mobile optimization)
- **Medium Devices (Tablets)**: 577px - 991px
- **Large Devices (Desktop)**: ≥992px

#### Mobile CSS Features
- **Touch-Friendly Elements**: Minimum 44px height for buttons and form controls
- **Mobile Typography**: Responsive font sizing that scales appropriately
- **iOS Zoom Prevention**: 16px minimum font size on form elements
- **Enhanced Navigation**: Mobile-optimized hamburger menu and navigation
- **Mobile Tables**: Stack-based table layout for small screens using `table-mobile-stack` class
- **Touch Gestures**: Optimized for touch devices with appropriate touch targets

#### Mobile Utility Classes
- `mobile-hide`: Hide elements on mobile devices
- `mobile-show`: Show elements only on mobile devices  
- `mobile-center`: Center align content on mobile
- `mobile-stack`: Stack child elements vertically on mobile
- `mobile-form-stack`: Stack form columns vertically on mobile
- `tablet-grid-2`: 2-column layout on tablets
- `tablet-form-stack`: Optimized form layouts for tablets

#### Responsive Table Pattern
For mobile-friendly tables, use the `table-mobile-stack` class:
```html
<div class="table-responsive">
    <table class="table table-mobile-stack">
        <thead>...</thead>
        <tbody>
            <tr>
                <td data-label="Vehicle">Car Details</td>
                <td data-label="Status">On Display</td>
                <td data-label="Price">R 250,000</td>
            </tr>
        </tbody>
    </table>
</div>
```

#### Dark Mode Mobile Support
- Mobile-specific dark mode adjustments
- Enhanced contrast for small screens
- Touch-friendly dark mode interactions

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
│   ├── Settings
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
7. **Settings**: Application configuration and preferences
8. **User Menu**: Profile, preferences, and logout

## Key Screens

### 1. Dashboard

![Dashboard](../app/static/img/docs/dashboard.png)

The dashboard provides a quick overview of the entire operation, with key metrics displayed prominently.

#### Key Metrics Cards

The dashboard includes several key metric cards that provide at-a-glance information about the current state of the business:

1. **Total Cars**: Displays the total number of cars currently in inventory
2. **Cars in Repair**: Shows how many cars are currently undergoing repairs
3. **Cars For Sale**: Indicates the number of cars currently on the sales stand
4. **Recent Sales**: Shows the number of cars sold in the last 30 days

#### Warning Cards

The dashboard also includes warning cards that highlight potential issues:

1. **Ready for Display**: Shows the count of cars that have completed repairs and are ready to be placed on a sales stand.
   - Displays the number of cars with status 'Ready for Display'
   - Shows the average reconditioning time (days from purchase to ready status)
   - Includes a "View Inventory" button that links to the inventory list with a filter applied
   - Helps identify cars that are ready for the next stage in the sales process

2. **Inventory Aging**: Shows vehicles that are approaching or exceeding the aging threshold on the sales stand. The card changes color based on severity:
   - Green: No vehicles exceeding threshold
   - Yellow: Vehicles approaching threshold
   - Red: Vehicles exceeding threshold
   
   The card includes a link to the Inventory Aging Report for more detailed information.

3. **Status Inactivity**: Warns about vehicles that have had no status change for an extended period:
   - Green: No vehicles with inactive status
   - Yellow: Vehicles approaching inactive threshold
   - Red: Vehicles exceeding inactive threshold
   
   The card includes a link to the Status Inactivity Report for more detailed information.

#### Profitability Metrics Card

The Profitability Metrics card displays key profit-related information for the last 30 days:

1. **Total Profit**: Shows the combined profit from all cars sold in the past 30 days, formatted as currency.
2. **Average ROI**: Displays the average Return on Investment percentage for cars sold in the past 30 days.

The card includes a link to the Profitability Report for more detailed information on sales performance and ROI calculations.

#### Top & Bottom Cars Profitability Card

The Top & Bottom Cars Profitability card provides a quick overview of the best and worst performing vehicles in terms of profit:

##### Mobile Optimizations
- **Responsive Layout**: Cards stack vertically on mobile devices
- **Touch-Friendly Tables**: Tables convert to mobile-friendly stacked layout on small screens
- **Condensed Buttons**: Button text is shortened on mobile with responsive visibility classes
- **Mobile Action Buttons**: Dashboard action buttons stack vertically and expand to full width on mobile

1. **Top 3 Cars by Profit**: Lists the three vehicles with the highest profit margin sold in the past 60 days.
   - Shows vehicle name, profit amount (in green), ROI percentage, status, and a link to the vehicle's profit report
   - Helps identify the most profitable vehicle models for future purchasing decisions

2. **Bottom Cars / Aging Inventory**: Lists the three vehicles that require attention due to either:
   - Poor profitability (recent sales with low or negative profit margins)
   - Aging inventory (vehicles on stand exceeding the aging threshold days)
   - Displays profit in red for negative values
   - Includes status indicators to distinguish between sold low-profit vehicles and aging inventory
   - Links to detailed profit reports for further analysis

The card provides a direct link to the full Profitability Report with a 60-day timeframe for more comprehensive analysis.

#### Stand Statistics

The Stand Statistics card shows:
1. **Cars per Stand**: A bar chart showing the number of cars on each stand
2. **Average Age of Cars**: A bar chart showing the average age (in days) of cars on each stand

The colors of the bars in the Average Age chart change based on the age of the cars relative to the aging threshold:
- Green: Average age is less than half the aging threshold
- Yellow: Average age is between half and full aging threshold
- Red: Average age exceeds the aging threshold

#### Activity Tables

The dashboard also includes several tables showing recent activity:

1. **Cars Waiting for Repair**: Shows cars that have been purchased but are not yet in the repair process
2. **Cars on Stand the Longest**: Shows cars that have been on the sales stand for the longest time
3. **Recent Repairs Completed**: Shows details of recently completed repairs

### 2. Inventory Management

#### 2.1 Vehicle List

![Vehicle List](../app/static/img/docs/vehicle_list.png)

- **Features**:
  - Filterable list of all vehicles
  - Status indicators (color-coded)
  - Quick action buttons
  - Search functionality
  - Status aging and inactivity warnings
  
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
  - Smart dropdowns for related data
  
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
  - Stand aging thresholds visualization
  
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
  - Total cost calculation
  - Status updates
  - Note management

- **Sections**:
  - Basic Information
  - Service Provider Details
  - Parts Used
  - Cost Breakdown
  - Notes and Attachments

#### 3.3 Repair Form

The repair form allows users to create and edit repair records with the following features:

- **Basic Information**:
  - Vehicle selection (dropdown with search)
  - Repair type selection
  - Provider selection
  - Date fields (start/end)
  - Cost entry
  - Notes

- **Parts Management**:
  - Add parts to the repair
  - Remove parts from the repair
  - Part cost tracking
  - Purchase date and vendor recording

- **Inventory Integration**:
  - Automatic part stock management
  - When a part is added to a repair:
    - If stock > 0: Stock is automatically decremented by 1
    - If stock = 0: A warning is displayed, but the part can still be used
  - When a part is removed from a repair:
    - Stock is automatically incremented by 1
  - When a part is changed during repair edit:
    - Old part's stock is incremented by 1
    - New part's stock is decremented by 1 (unless at 0)
  - Stock levels never go negative
  - Warning messages are displayed when using parts with zero stock

- **Validation**:
  - Required fields enforcement
  - Date validation (start before end)
  - Cost validation (positive numbers)
  - Status change validation

#### 3.4 Parts Management

![Parts Management](../app/static/img/docs/parts_management.png)

- **Features**:
  - Inventory of parts
  - Usage tracking
  - Add/Edit part controls
  - Duplicate detection and stock merging
  
- **Elements**:
  - Parts list with search
  - Stock level indicators
  - Cost history
  - Usage reports

##### Part Creation & Duplication Handling

When adding a new part, the system provides intelligent duplicate detection:

- **Part Duplicate Detection**: 
  - When a user submits a new part, the system checks if a part with the same name, make, and model already exists
  - The comparison is case-insensitive and space-insensitive for better matching
  - The system takes into account vehicle targeting (make and model) when determining duplicates

- **Duplicate Handling Behavior**:
  - If a duplicate is found, the system increases the stock quantity of the existing part by the submitted amount
  - The system optionally updates other fields (description, price, etc.) if they were provided
  - A confirmation message "Part already exists — stock updated" is displayed
  - No new database record is created

- **New Part Creation**:
  - If no duplicate is found, a new part is created normally
  - A confirmation message "New part added" is displayed

- **Subform Integration**:
  - When adding a part through a subform (like during repair creation):
    - The duplicate detection still applies
    - After updating an existing part or creating a new one, the part is immediately available for selection
    - The newly created or updated part is automatically selected in the parent form

This intelligent duplicate handling ensures inventory accuracy while providing a seamless user experience.

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
  - Customer details
  - Commission calculation
  
- **Sections**:
  - Sale Information
  - Vehicle Details
  - Financial Summary
  - Customer Information
  - Dealer Details
  - Notes and Documentation

### 5. Settings Management

![Settings](../app/static/img/docs/settings.png)

- **Features**:
  - Tabbed interface for different setting categories
  - Save changes in each tab independently
  - Live preview for certain settings
  
- **Tabs**:
  - **General Configuration**:
    - Enable Dark Mode toggle
    - UI preferences
    - Display options
  
  - **Thresholds & Rules**:
    - Stand aging threshold (days)
    - Status inactivity threshold (days)
    - Enable depreciation tracking toggle
    - Enable status warnings toggle
    - Enable subform dropdowns toggle
  
  - **User Management**:
    - User list with roles
    - Add/Edit/Delete user controls
    - Password reset functionality
    - Role assignment

### 6. Bulk Import

![Import](../app/static/img/docs/import.png)

- **Features**:
  - Tabbed interface for different entity imports
  - Template downloads for each entity type
  - File upload with validation
  - Import results summary
  
- **Import Types**:
  - Cars
  - Repairs
  - Sales
  - Dealers
  - Parts
  - Stands
  
- **Functionality**:
  - Select file (CSV or Excel)
  - Upload and validate
  - View import results
  - Error reporting for failed rows

## Form Components

### Smart Dropdowns

The application uses enhanced select dropdowns with the following features:

- **Search functionality**: Type to search for options
- **Create new option**: Add new entries directly from the dropdown
- **Categorized options**: Group options by type or category
- **Recent selections**: Quick access to recently used options
- **Validation feedback**: Inline error messages for invalid selections

Example implementation:
```html
<div class="form-group">
  <label for="vehicle_make">Make</label>
  <select 
    class="form-control smart-dropdown" 
    id="vehicle_make" 
    name="vehicle_make"
    data-create-new="true"
    data-api-url="/api/vehicle-makes"
  >
    <option value="">Select Make</option>
    {% for make in makes %}
      <option value="{{ make.id }}">{{ make.name }}</option>
    {% endfor %}
  </select>
  <small class="form-text text-muted">Start typing to search or create a new make</small>
</div>
```

### Subform Modals

The application uses modal dialogs for creating related entities without leaving the current form:

- **Triggered from parent form**: Button to open modal directly from main form
- **Inline validation**: Real-time validation of subform inputs
- **Automatic integration**: On submit, adds new entity to parent form dropdown
- **Cancel without side effects**: Close without affecting parent form state

Example implementation:
```html
<!-- Trigger button in parent form -->
<button type="button" class="btn btn-sm btn-outline-primary" data-toggle="modal" data-target="#addMakeModal">
  <i class="fas fa-plus"></i> Add New Make
</button>

<!-- Modal implementation -->
<div class="modal fade" id="addMakeModal" tabindex="-1" role="dialog" aria-labelledby="addMakeModalTitle" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="addMakeModalTitle">Add New Vehicle Make</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        <form id="makeForm">
          <div class="form-group">
            <label for="makeName">Make Name</label>
            <input type="text" class="form-control" id="makeName" required>
          </div>
        </form>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
        <button type="button" class="btn btn-primary" id="saveMake">Save</button>
      </div>
    </div>
  </div>
</div>
```

### Form Validation

The application implements multi-layered validation:

1. **Client-side validation**:
   - HTML5 form validation (`required`, `pattern`, etc.)
   - JavaScript validation for complex rules
   - Real-time feedback as user types

2. **Server-side validation**:
   - Input sanitization to prevent security issues
   - Business rule validation
   - Database constraint checks

3. **Validation feedback**:
   - Inline error messages
   - Field highlighting
   - Form-level error summaries
   - Input correction suggestions

## UI Components

### Status Indicators

The application uses color-coded status indicators throughout:

- **Green**: Completed, active, or available
- **Yellow**: In progress or requiring attention
- **Red**: Critical issues, overdue, or errors
- **Gray**: Inactive or archived

Example implementation:
```html
<span class="status-badge status-{{ status.lower() }}">
  {{ status }}
</span>
```

With CSS:
```css
.status-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: bold;
}
.status-sold { background-color: #28a745; color: white; }
.status-on-display { background-color: #17a2b8; color: white; }
.status-in-repair { background-color: #ffc107; color: black; }
.status-waiting-for-repairs { background-color: #dc3545; color: white; }
```

### Data Tables

The application uses enhanced data tables with the following features:

- **Pagination**: Control number of items per page
- **Sorting**: Click column headers to sort
- **Filtering**: Filter table content by various criteria
- **Export**: Download data as CSV or Excel
- **Column visibility**: Toggle which columns are displayed
- **Row actions**: Dropdown or button actions for each row

### Dark Mode

The application supports a dark theme which can be toggled through settings:

- **Dark background** with light text
- **Reduced contrast** for long working sessions
- **Preserved readability** of all UI elements
- **Consistent styling** across all pages
- **User preference storage** in browser and account settings

The dark mode implementation uses CSS variables and a theme class:

```css
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --text-primary: #212529;
  --text-secondary: #6c757d;
  --border-color: #dee2e6;
}

.dark-theme {
  --bg-primary: #212529;
  --bg-secondary: #343a40;
  --text-primary: #f8f9fa;
  --text-secondary: #adb5bd;
  --border-color: #495057;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-primary);
}
```

## Mobile Responsiveness

The application is designed to be responsive across different device sizes:

- **Desktop**: Full layout with multiple columns and detailed information
- **Tablet**: Adjusted layout with some elements moved or collapsed
- **Mobile**: Simplified layout with essential information and touch-friendly controls

Key mobile design considerations:
- **Larger touch targets** for buttons and controls
- **Simplified tables** with fewer columns
- **Collapsible sections** to focus on important information
- **Bottom navigation bar** for key actions
- **Reduced data load** to improve performance

## Accessibility Features

The application implements accessibility best practices:

- **ARIA attributes** for screen readers
- **Keyboard navigation** support
- **Sufficient color contrast** for all text
- **Focus indicators** for keyboard users
- **Text alternatives** for images
- **Skip to content** links

## User Experience Flow

The application is designed around common user workflows:

1. **Adding a new vehicle**:
   - Navigate to Inventory > Add Vehicle
   - Fill in vehicle details with standardized makes/models
   - Save vehicle (initially in "Waiting for Repairs" status)
   - Optionally add repair record from confirmation screen

2. **Processing repairs**:
   - Navigate to Repairs > Add Repair or from vehicle detail page
   - Select vehicle and add repair details
   - Add parts using subform modal if needed
   - Update repair status as it progresses
   - Complete repair (updates vehicle status to "Ready for Display")

3. **Adding vehicle to stand**:
   - Navigate to Inventory > Stand Management
   - Drag vehicle from available vehicles to a stand
   - Or update vehicle directly from detail page
   - System automatically updates status to "On Display"

4. **Recording a sale**:
   - Navigate to Sales > New Sale or from vehicle detail page
   - Select vehicle (must be "On Display" status)
   - Enter sale details
   - Save sale (automatically updates vehicle status to "Sold")

5. **Generating reports**:
   - Navigate to Reports
   - Select report type
   - Configure parameters and filters
   - Generate and view report
   - Optionally export or schedule recurring reports 