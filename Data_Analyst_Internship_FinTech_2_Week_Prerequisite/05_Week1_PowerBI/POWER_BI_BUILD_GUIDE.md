# Power BI Dashboard – Build Guide

1. Open Power BI Desktop.
2. Get Data → Text/CSV → `sales_dashboard_data.csv`.
3. Set `order_date` to Date and numeric fields to Decimal/Whole Number.
4. Create the measures in `starter_measures.dax`.
5. Create:
   - KPI cards for Total Sales, Total Profit, Orders, Customers.
   - Line chart: Month → Total Sales.
   - Bar chart: Product → Total Sales.
   - Bar chart: State → Total Sales.
   - Donut: City Tier → Total Sales.
6. Add slicers for Date, State, Product and City Tier.
7. Add a title: `Sales Performance Dashboard`.
8. Save as `Data_Analyst_Sales_Dashboard.pbix`.

The PBIX itself cannot be generated reliably outside Power BI Desktop, so this folder is intentionally Power BI-ready rather than a fake PBIX.
