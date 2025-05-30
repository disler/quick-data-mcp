# Sample Datasets for Analytics MCP Server

This directory contains sample datasets for testing and demonstrating the generic data analytics MCP server capabilities.

## Datasets

### 1. E-commerce Orders (`ecommerce_orders.json`)
- **Description**: Sample e-commerce transaction data
- **Format**: JSON
- **Rows**: 15 orders
- **Use Cases**: Sales analysis, customer segmentation, regional performance
- **Key Columns**:
  - `order_value` (numerical): Order amount in USD
  - `product_category` (categorical): Product type
  - `region` (categorical): Geographic region
  - `customer_segment` (categorical): Customer tier
  - `order_date` (temporal): Transaction date

### 2. Employee Survey (`employee_survey.csv`)
- **Description**: Employee satisfaction and workforce data
- **Format**: CSV
- **Rows**: 25 employees
- **Use Cases**: HR analytics, satisfaction analysis, departmental comparisons
- **Key Columns**:
  - `satisfaction_score` (numerical): Employee satisfaction (1-10)
  - `tenure_years` (numerical): Years with company
  - `department` (categorical): Work department
  - `remote_work` (categorical): Work arrangement
  - `salary_band` (categorical): Compensation level

### 3. Product Performance (`product_performance.csv`)
- **Description**: Product sales and inventory metrics
- **Format**: CSV
- **Rows**: 20 products
- **Use Cases**: Product analysis, inventory optimization, supplier evaluation
- **Key Columns**:
  - `monthly_sales` (numerical): Units sold per month
  - `inventory_level` (numerical): Current stock
  - `rating` (numerical): Customer rating (1-5)
  - `category` (categorical): Product category
  - `supplier` (categorical): Supplier name
  - `launch_date` (temporal): Product launch date

## Usage Examples

### Loading Datasets
```python
# Load e-commerce data
load_dataset('data/ecommerce_orders.json', 'ecommerce')

# Load employee survey
load_dataset('data/employee_survey.csv', 'employees')

# Load product data
load_dataset('data/product_performance.csv', 'products')
```

### Analysis Examples

#### Segmentation Analysis
```python
# Analyze orders by region
segment_by_column('ecommerce', 'region')

# Compare employees by department
segment_by_column('employees', 'department')

# Group products by category
segment_by_column('products', 'category')
```

#### Correlation Analysis
```python
# Find relationships in employee data
find_correlations('employees')

# Analyze product metrics
find_correlations('products', ['monthly_sales', 'rating', 'inventory_level'])
```

#### Visualization
```python
# Order value distribution
create_chart('ecommerce', 'histogram', 'order_value')

# Sales by product category
create_chart('products', 'bar', 'category', 'monthly_sales')

# Satisfaction vs tenure
create_chart('employees', 'scatter', 'tenure_years', 'satisfaction_score')
```

#### Time Series Analysis
```python
# Order trends over time
time_series_analysis('ecommerce', 'order_date', 'order_value')

# Product launch timeline
time_series_analysis('products', 'launch_date', 'monthly_sales')
```

#### Data Quality Assessment
```python
# Check data quality
validate_data_quality('ecommerce')
validate_data_quality('employees')
validate_data_quality('products')
```

## Dataset Characteristics

| Dataset | Numerical Cols | Categorical Cols | Temporal Cols | Suggested Analyses |
|---------|----------------|------------------|---------------|-------------------|
| E-commerce | 1 | 5 | 1 | Segmentation, Time Series |
| Employees | 2 | 3 | 0 | Correlation, Segmentation |
| Products | 3 | 3 | 1 | Correlation, Time Series |

## Testing Scenarios

These datasets are designed to test various analytics capabilities:

1. **Schema Discovery**: Different data types and formats
2. **Segmentation**: Multiple categorical variables for grouping
3. **Correlation**: Numerical relationships to explore
4. **Time Series**: Date columns for temporal analysis
5. **Data Quality**: Clean data with good coverage
6. **Visualization**: Various chart types and combinations
7. **Cross-Dataset**: Potential for merging and comparison

## Extending the Datasets

You can modify these datasets or add new ones by:
1. Adding more rows for larger-scale testing
2. Introducing missing values to test data quality features
3. Creating related datasets for merge testing
4. Adding more numerical columns for advanced correlation analysis
5. Including text columns for natural language processing features