# Sample Datasets

This directory contains sample datasets for testing and demonstration purposes.

## Available Datasets

### ecommerce_orders.json
E-commerce order data with customer transactions.

**Structure:**
- `order_id`: Unique order identifier
- `customer_id`: Customer identifier
- `order_date`: Date of order
- `product_category`: Product category name
- `product_name`: Product name
- `quantity`: Number of items ordered
- `unit_price`: Price per unit
- `order_value`: Total order value
- `payment_method`: Payment type used
- `shipping_address`: Delivery address
- `order_status`: Current order status
- `delivery_date`: Actual delivery date

**Usage Example:**
```python
await load_dataset(
    file_path="data/ecommerce_orders.json",
    dataset_name="orders"
)

# Analyze by category
await segment_by_column(
    dataset_name="orders",
    column_name="product_category"
)
```

### employee_survey.csv
Employee satisfaction survey results.

**Structure:**
- `employee_id`: Employee identifier
- `department`: Department name
- `years_at_company`: Tenure in years
- `satisfaction_score`: Overall satisfaction (1-10)
- `work_life_balance`: Work-life balance rating (1-10)
- `compensation_satisfaction`: Compensation satisfaction (1-10)
- `career_development`: Career development opportunities (1-10)
- `management_quality`: Management quality rating (1-10)
- `would_recommend`: Would recommend company (Yes/No)
- `survey_date`: Date survey was completed

**Usage Example:**
```python
await load_dataset(
    file_path="data/employee_survey.csv",
    dataset_name="survey"
)

# Find correlations
await find_correlations(
    dataset_name="survey",
    threshold=0.3
)
```

### product_performance.csv
Product sales and performance metrics.

**Structure:**
- `product_id`: Product identifier
- `product_name`: Product name
- `category`: Product category
- `launch_date`: Product launch date
- `monthly_sales`: Sales for the month
- `revenue`: Revenue generated
- `profit_margin`: Profit margin percentage
- `customer_rating`: Average customer rating (1-5)
- `return_rate`: Product return rate
- `inventory_level`: Current inventory
- `marketing_spend`: Marketing expenditure
- `competitive_index`: Market competitiveness score

**Usage Example:**
```python
await load_dataset(
    file_path="data/product_performance.csv",
    dataset_name="products"
)

# Time series analysis
await time_series_analysis(
    dataset_name="products",
    date_column="launch_date",
    value_column="monthly_sales"
)
```

## Additional Datasets

The directory also contains real estate datasets:
- `zillow_rent_data.csv` - Rental price data by region
- `zillow_home_values_*.csv` - Home value data for various cities
- `n_movies.csv` - Movie dataset for entertainment analytics

## Testing with Sample Data

These datasets are used in the test suite to validate all analytics functions:

```bash
# Run tests using sample data
uv run python -m pytest tests/ -v
```

The test suite validates:
- Data loading and parsing
- Statistical calculations
- Visualization generation
- Data quality checks
- Cross-dataset operations