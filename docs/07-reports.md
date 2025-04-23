# Reports

This document details the reporting system in the Car Repair and Sales Tracking Application.

## Report Categories

The application offers the following report categories:

1. **Financial Reports** - Track revenue, costs, profits, and financial KPIs
2. **Inventory Reports** - Monitor vehicle status, aging, and turnover
3. **Sales Reports** - Analyze sales performance, trends, and dealer metrics
4. **Repair Reports** - Evaluate repair efficiency, costs, and provider performance
5. **Custom Reports** - Build and save custom reports with user-defined parameters

## Implementation Status

The reporting system is implemented with varying levels of completion:

| Report Category | Implementation Status | Notes |
|----------------|------------------------|-------|
| Financial Reports | Complete | All core financial reports are implemented |
| Inventory Reports | Complete | All inventory reports are implemented with aging thresholds |
| Sales Reports | Complete | All sales reports are implemented |
| Repair Reports | Partial | Basic repair reports implemented, advanced analytics in development |
| Custom Reports | In Development | Framework in place, UI for report building in progress |

## Financial Reports

### Profit and Loss Report

**Status: Complete**

**Purpose:** Provide a comprehensive view of business financial performance.

**Key Metrics:**
- Total Revenue (sales price of all vehicles sold)
- Total Costs (purchase price + repair costs + other expenses)
- Gross Profit (revenue - costs)
- Profit Margin (gross profit / revenue)
- Commission Expenses

**Filters:**
- Date Range (daily, weekly, monthly, quarterly, yearly, custom)
- Vehicle Type
- Dealer

### Vehicle Profitability Report

**Status: Complete**

**Purpose:** Analyze profitability of individual vehicles or vehicle types.

**Key Metrics:**
- Purchase Price
- Total Repair Cost
- Total Investment
- Sale Price
- Profit
- Profit Margin
- Days to Sell
- Return on Investment (ROI)

**New Feature:** ROI calculation has been added to provide better investment analysis.

## Inventory Reports

### Current Inventory Report

**Status: Complete**

**Purpose:** Provide snapshot of current inventory status.

**Key Metrics:**
- Total Vehicles in Inventory
- Vehicles by Status (Waiting for Repairs, In Repair, Ready for Display, On Display)
- Vehicles by Location
- Average Days in Inventory
- Total Investment in Current Inventory

**Enhanced Feature:** Status inactivity warnings based on configurable threshold.

### Inventory Aging Report

**Status: Complete**

**Purpose:** Identify vehicles that have been in inventory for extended periods.

**Key Metrics:**
- Days in Inventory
- Current Status
- Total Investment
- Location
- Suggested Action (based on age thresholds)

**Age Categories:**
- 0-30 days: Normal
- 31-60 days: Monitor
- 61-90 days: Review Pricing
- 91+ days: Consider Discounting or Wholesale

**Enhanced Feature:** Configurable aging thresholds via Settings page.

### Vehicle Depreciation Report

**Status: Available when enabled**

**Purpose:** Track estimated value depreciation of vehicles over time.

**Key Metrics:**
- Original Investment
- Current Estimated Value
- Depreciation Amount
- Depreciation Percentage
- Days in Inventory

**Note:** This report is only available when depreciation tracking is enabled in Settings.

## Sales Reports

### Dealer Performance Report

**Status: Complete**

**Purpose:** Evaluate and compare dealer sales performance.

**Key Metrics:**
- Total Sales (count)
- Total Revenue
- Total Profit Generated
- Average Profit per Sale
- Commission Earned
- Sales Velocity (average days from display to sale)

### Sales Trend Report

**Status: Complete**

**Purpose:** Analyze sales patterns over time.

**Key Metrics:**
- Sales Count by Period
- Revenue by Period
- Profit by Period
- Average Sale Price by Period
- Seasonal Patterns

**Visualization:**
- Line charts for trends over time
- Bar charts for period comparisons
- Heatmaps for identifying patterns

### Make/Model Performance Report

**Status: Complete**

**Purpose:** Analyze sales performance by vehicle make and model.

**Key Metrics:**
- Total Sales by Make
- Total Sales by Model
- Profit Margin by Make/Model
- Average Days to Sell by Make/Model
- Most Profitable Makes/Models

## Repair Reports

### Repair Efficiency Report

**Status: Complete**

**Purpose:** Evaluate repair process efficiency.

**Key Metrics:**
- Average Repair Duration
- Average Repair Cost
- Repair Cost Distribution
- Most Common Repair Types
- Provider Performance Comparison

### Parts Usage Report

**Status: Partial - Basic reporting only**

**Purpose:** Track parts usage and cost analysis.

**Key Metrics:**
- Most Used Parts
- Parts Cost Distribution
- Parts Usage by Repair Type
- Parts Inventory Status

**In Development:** Advanced parts inventory tracking and forecasting.

### Provider Performance Report

**Status: In Development**

**Purpose:** Compare and evaluate repair provider performance.

**Planned Metrics:**
- Average Repair Duration by Provider
- Average Cost per Repair Type
- Quality Rating (based on need for follow-up repairs)
- On-time Completion Rate

## Custom Reports

**Status: In Development**

The application framework includes:

1. **Field Selection** - Backend code for selecting fields
2. **Filtering Criteria** - API for filtering data
3. **Grouping Options** - Backend support for data aggregation
4. **Sorting** - API endpoints for sorted data retrieval

**In Development:**
1. **User Interface** - Visual report builder
2. **Report Saving** - Saving custom report configurations
3. **Scheduling** - Automated report generation and delivery

## Report Export Options

The following export options are implemented:

1. **PDF** - For formal presentation and printing (Complete)
2. **CSV** - For data analysis in spreadsheet applications (Complete)
3. **Excel** - For advanced data manipulation (Complete)
4. **JSON** - For integration with other systems (In Development)

## Report Scheduling

**Status: Planned for Future Release**

The application plans to allow reports to be scheduled for automatic generation:

1. **Frequency Options:**
   - Daily
   - Weekly
   - Monthly
   - Quarterly
   - Yearly

2. **Delivery Methods:**
   - Email
   - File Share
   - Dashboard Alert

## Report Permissions

**Status: Complete for Basic Permission Control**

Reports have permission settings to control:

1. **Visibility** - Role-based access to different report types
2. **Editing** - Admin-only ability to modify report configurations
3. **Scheduling** - Admin-only ability to schedule reports (future feature)
4. **Exporting** - Role-based ability to export reports

## Dashboard Integration

**Status: Partial Implementation**

Reports can be added to dashboards:

1. **Widgets** - Display report data as dashboard widgets (Complete)
2. **Auto-refresh** - Set widgets to refresh at defined intervals (In Development)
3. **Drill-down** - Click widgets to view detailed report data (Complete)
4. **Layout Customization** - Arrange widgets as needed (In Development)

## Report Implementation

The application implements reports using:

1. **Data Access Layer** - SQL queries using SQLAlchemy ORM
2. **Business Logic Layer** - Data processing and calculations
3. **Presentation Layer** - Rendering with templates and charts
4. **Export Layer** - Format conversion for different outputs

## Configurable Report Thresholds

Reports are influenced by system settings configured in the Settings page:

1. **Inventory Aging Thresholds** - The `stand_aging_threshold_days` setting determines when vehicles are flagged as aging in inventory reports. This threshold affects:
   - The color coding in the Inventory Aging Report
   - Warning indicators in the Current Inventory Report
   - Suggested action recommendations

2. **Status Inactivity Warnings** - The `status_inactivity_threshold_days` setting controls when vehicles are highlighted for having remained in the same status too long, affecting:
   - Operational efficiency metrics
   - Status timeline visualizations
   - Workflow bottleneck identification

3. **Feature Toggles** - Several report features can be enabled or disabled through settings:
   - When `enable_depreciation_tracking` is enabled, reports include depreciation calculations
   - When `enable_status_warnings` is enabled, reports include status warning indicators
   - UI appearance changes based on the `enable_dark_mode` setting

4. **Settings Access** - Report configuration thresholds can be adjusted by administrators through the Settings page, allowing the business to tune reporting behavior to their specific needs without code changes. 