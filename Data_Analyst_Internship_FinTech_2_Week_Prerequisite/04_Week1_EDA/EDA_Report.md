# EDA Report – Sample Sales Dataset

## Dataset
- Rows after cleaning: **600**
- Unique orders: **600**
- Unique customers: **80**
- Date range: **2026-01-01 to 2026-06-30**
- Duplicate order IDs after cleaning: **0**

## Cleaning performed
1. Removed duplicate `order_id` records.
2. Filled missing `city` and `product` with `Unknown`.
3. Converted dates and numeric fields to appropriate types.
4. Validated order, customer and sales fields.

## Key business KPIs
- Total sales: **₹27,297,550.80**
- Total profit: **₹5,411,320.21**
- Average order value: **₹45,495.92**
- Profit margin: **19.82%**

## Findings
- The product summary identifies the products contributing the largest revenue.
- State-level aggregation shows geographic concentration of sales.
- Monthly aggregation can be used to identify changes in sales volume over time.
- Profit margin should be monitored alongside revenue so high-sales products are not evaluated on revenue alone.

## Limitations
This is a **synthetic sample dataset created for prerequisite practice**. It is not company or customer data and should not be presented as real business data.
