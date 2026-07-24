import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("charts", exist_ok=True)
sns.set_style("whitegrid")

df = pd.read_csv("/mnt/user-data/uploads/DataCoSupplyChainDataset.csv", encoding="latin1")

print("Number of rows and columns:", df.shape)
print("\nMissing values in each column:")
print(df.isnull().sum()[df.isnull().sum() > 0])

columns_to_remove = [
    "Product Description", "Customer Email", "Customer Password",
    "Customer Fname", "Customer Lname", "Customer Street",
    "Product Image", "Order Zipcode"
]

df = df.drop(columns=columns_to_remove, errors="ignore")

df["order date (DateOrders)"] = pd.to_datetime(df["order date (DateOrders)"])
df["shipping date (DateOrders)"] = pd.to_datetime(df["shipping date (DateOrders)"])

df["Customer Zipcode"] = df["Customer Zipcode"].fillna(0)

df = df.drop_duplicates()

print("\nData cleaned. New shape:", df.shape)

df["Order Year"] = df["order date (DateOrders)"].dt.year
df["Order Month"] = df["order date (DateOrders)"].dt.strftime("%B")
df["Delivery Delay"] = (
    df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
)
df["Is Canceled"] = df["Order Status"].isin(["CANCELED", "SUSPECTED_FRAUD"])

sales_by_category = (
    df.groupby("Category Name")[["Sales", "Order Profit Per Order"]]
    .sum()
    .sort_values("Sales", ascending=False)
)

print("\nTop 10 categories by sales:")
print(sales_by_category.head(10))

top10_categories = sales_by_category.head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=top10_categories["Sales"], y=top10_categories.index)
plt.title("Top 10 Categories by Sales")
plt.xlabel("Total Sales ($)")
plt.savefig("charts/01_top_categories.png", bbox_inches="tight")
plt.close()

profit_by_region = (
    df.groupby("Order Region")["Order Profit Per Order"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 5 regions by profit:")
print(profit_by_region.head(5))

plt.figure(figsize=(12, 6))
sns.barplot(x=profit_by_region.index, y=profit_by_region.values)
plt.title("Profit by Region")
plt.xticks(rotation=75, ha="right")
plt.savefig("charts/02_profit_by_region.png", bbox_inches="tight")
plt.close()

spending_by_customer = (
    df.groupby("Customer Id")["Sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 10 customers by spending:")
print(spending_by_customer.head(10))

orders_per_customer = df.groupby("Customer Id")["Order Id"].nunique()
order_frequency = orders_per_customer.value_counts().sort_index()

plt.figure(figsize=(7, 7))
order_frequency.head(5).plot.pie(autopct="%1.0f%%", ylabel="")
plt.title("How Often Customers Order")
plt.savefig("charts/03_order_frequency.png", bbox_inches="tight")
plt.close()

delivery_status_count = df["Delivery Status"].value_counts()

print("\nDelivery status counts:")
print(delivery_status_count)

plt.figure(figsize=(7, 7))
delivery_status_count.plot.pie(autopct="%1.1f%%", ylabel="")
plt.title("Delivery Status Breakdown")
plt.savefig("charts/04_delivery_status.png", bbox_inches="tight")
plt.close()

delay_by_shipping_mode = df.groupby("Shipping Mode")["Delivery Delay"].mean()

print("\nAverage delay by shipping mode:")
print(delay_by_shipping_mode)

profit_sorted = sales_by_category.sort_values(
    "Order Profit Per Order", ascending=False
)

print("\nMost profitable category:", profit_sorted.index[0])
print("Least profitable category:", profit_sorted.index[-1])

profit_by_product = (
    df.groupby("Product Name")["Order Profit Per Order"]
    .sum()
    .sort_values(ascending=False)
)

print("\nTop 10 most profitable products:")
print(profit_by_product.head(10))

plt.figure(figsize=(10, 6))
sns.barplot(
    x=profit_by_product.head(10).values,
    y=profit_by_product.head(10).index
)
plt.title("Top 10 Most Profitable Products")
plt.xlabel("Total Profit ($)")
plt.savefig("charts/05_top_products.png", bbox_inches="tight")
plt.close()

discount_profit_correlation = df["Order Item Discount Rate"].corr(
    df["Order Profit Per Order"]
)

print(
    f"\nCorrelation between discount rate and profit: "
    f"{discount_profit_correlation:.3f}"
)

profit_by_year = (
    df.groupby("Order Year")["Order Profit Per Order"]
    .sum()
)

print("\nProfit by year:")
print(profit_by_year)

plt.figure(figsize=(8, 6))
sns.barplot(x=profit_by_year.index, y=profit_by_year.values)
plt.title("Total Profit by Year")
plt.savefig("charts/06_profit_by_year.png", bbox_inches="tight")
plt.close()

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

orders_by_month = (
    df.groupby("Order Month")["Order Id"]
    .nunique()
    .reindex(month_order)
)

plt.figure(figsize=(10, 6))
orders_by_month.plot(kind="line", marker="o")
plt.title("Number of Orders by Month")
plt.xticks(rotation=45)
plt.savefig("charts/07_orders_by_month.png", bbox_inches="tight")
plt.close()

order_status_count = df["Order Status"].value_counts()

print("\nOrder status counts:")
print(order_status_count)

cancellation_rate = df["Is Canceled"].mean() * 100

print(f"\nCancellation rate: {cancellation_rate:.2f}%")

plt.figure(figsize=(9, 6))
sns.barplot(x=order_status_count.values, y=order_status_count.index)
plt.title("Order Status Breakdown")
plt.savefig("charts/08_order_status.png", bbox_inches="tight")
plt.close()

print("\n===== KEY INSIGHTS =====")
print(f"1. Top selling category: {sales_by_category.index[0]}")
print(f"2. Most profitable region: {profit_by_region.index[0]}")
print(f"3. Top customer ID: {spending_by_customer.index[0]}")
print(f"4. Most profitable product: {profit_by_product.index[0]}")
print(
    f"5. Discount vs profit correlation: "
    f"{discount_profit_correlation:.2f} (very weak)"
)
print(f"6. Cancellation rate: {cancellation_rate:.2f}%")
print(f"7. Best year for profit: {profit_by_year.idxmax()}")
print(f"8. Busiest month for orders: {orders_by_month.idxmax()}")

print("\nAll charts saved in the 'charts' folder.")