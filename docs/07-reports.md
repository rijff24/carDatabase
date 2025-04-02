# Reports

This document details the reporting system in the Car Repair and Sales Tracking Application.

## Report Categories

The application offers the following report categories:

1. **Financial Reports** - Track revenue, costs, profits, and financial KPIs
2. **Inventory Reports** - Monitor vehicle status, aging, and turnover
3. **Sales Reports** - Analyze sales performance, trends, and dealer metrics
4. **Repair Reports** - Evaluate repair efficiency, costs, and provider performance
5. **Custom Reports** - Build and save custom reports with user-defined parameters

## Financial Reports

### Profit and Loss Report

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

## Inventory Reports

### Current Inventory Report

**Purpose:** Provide snapshot of current inventory status.

**Key Metrics:**
- Total Vehicles in Inventory
- Vehicles by Status (Waiting for Repairs, In Repair, Ready for Display, On Display)
- Vehicles by Location
- Average Days in Inventory
- Total Investment in Current Inventory

### Inventory Aging Report

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

## Sales Reports

### Dealer Performance Report

**Purpose:** Evaluate and compare dealer sales performance.

**Key Metrics:**
- Total Sales (count)
- Total Revenue
- Total Profit Generated
- Average Profit per Sale
- Commission Earned
- Sales Velocity (average days from display to sale)

### Sales Trend Report

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

## Repair Reports

### Repair Efficiency Report

**Purpose:** Evaluate repair process efficiency.

**Key Metrics:**
- Average Repair Duration
- Average Repair Cost
- Repair Cost Distribution
- Most Common Repair Types
- Provider Performance Comparison

### Parts Usage Report

**Purpose:** Track parts usage and cost analysis.

**Key Metrics:**
- Most Used Parts
- Parts Cost Distribution
- Parts Usage by Repair Type
- Parts Inventory Status

## Custom Reports

The application allows users to create custom reports with:

1. **Field Selection** - Choose which fields to include
2. **Filtering Criteria** - Set custom filters
3. **Grouping Options** - Determine how data is aggregated
4. **Sorting** - Order results as needed
5. **Visualization Type** - Select appropriate charts
6. **Scheduling** - Set up automatic report generation
7. **Report Sharing** - Define who receives reports

## Report Export Options

Reports can be exported in the following formats:

1. **PDF** - For formal presentation and printing
2. **CSV** - For data analysis in spreadsheet applications
3. **Excel** - For advanced data manipulation
4. **JSON** - For integration with other systems

## Report Scheduling

The application allows reports to be scheduled for automatic generation:

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

Reports have permission settings to control:

1. **Visibility** - Who can see the report
2. **Editing** - Who can modify the report
3. **Scheduling** - Who can schedule the report
4. **Exporting** - Who can export the report

## Dashboard Integration

Reports can be added to customizable dashboards:

1. **Widgets** - Display report data as dashboard widgets
2. **Auto-refresh** - Set widgets to refresh at defined intervals
3. **Drill-down** - Click widgets to view detailed report data
4. **Layout Customization** - Arrange widgets as needed

## Report Implementation

The application implements reports using:

1. **Data Access Layer** - SQL queries using SQLAlchemy ORM
2. **Business Logic Layer** - Data processing and calculations
3. **Presentation Layer** - Rendering with templates and charts
4. **Export Layer** - Format conversion for different outputs

## Configurable Report Thresholds

Reports are influenced by system settings configured in the System Settings page:

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