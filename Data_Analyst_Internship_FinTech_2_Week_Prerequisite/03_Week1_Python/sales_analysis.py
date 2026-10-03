import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path("../01_Week1_Excel/data/sample_sales_cleaned.csv")
df = pd.read_csv(DATA, parse_dates=["order_date"])

# Basic validation
print(df.shape)
print(df.isna().sum())
print("Duplicate order IDs:", df["order_id"].duplicated().sum())

# KPIs
total_sales = df["sales_amount"].sum()
total_profit = df["profit"].sum()
orders = df["order_id"].nunique()
customers = df["customer_id"].nunique()
aov = df["sales_amount"].mean()

print(f"Total sales: ₹{total_sales:,.2f}")
print(f"Total profit: ₹{total_profit:,.2f}")
print(f"Orders: {orders:,}")
print(f"Customers: {customers:,}")
print(f"Average order value: ₹{aov:,.2f}")

# Product and state analysis
product_summary = df.groupby("product").agg(
    revenue=("sales_amount","sum"),
    units=("quantity","sum"),
    profit=("profit","sum")
).sort_values("revenue", ascending=False)
print(product_summary)

monthly = df.groupby(df["order_date"].dt.to_period("M"))["sales_amount"].sum()
monthly.plot(kind="line", marker="o", title="Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.tight_layout()
plt.savefig("monthly_sales.png", dpi=160)
plt.show()

state_summary = df.groupby("state")["sales_amount"].sum().sort_values(ascending=False)
state_summary.plot(kind="bar", title="Sales by State")
plt.ylabel("Sales")
plt.tight_layout()
plt.savefig("sales_by_state.png", dpi=160)
plt.show()
