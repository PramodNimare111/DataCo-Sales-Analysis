"""
DataCo Supply Chain - Data Analytics Project
This script loads the data, cleans it, analyzes it, and creates charts.
"""

# Import the libraries we need
import pandas as pd              # for working with tables of data
import matplotlib.pyplot as plt  # for making charts
import seaborn as sns            # for nicer looking charts
import os                        # for creating folders

# Make a folder to save our charts in
os.makedirs("charts", exist_ok=True)
sns.set_style("whitegrid")


# ==========================================================
# STEP 1: LOAD THE DATA
# ==========================================================

# encoding="latin1" is used because the file has special characters
# (like accented letters in country names)
df = pd.read_csv("/mnt/user-data/uploads/DataCoSupplyChainDataset.csv", encoding="latin1")

print("Number of rows and columns:", df.shape)
print("\nMissing values in each column:")
print(df.isnull().sum()[df.isnull().sum() > 0])


# ==========================================================
# STEP 2: CLEAN THE DATA
# ==========================================================

# Remove columns we don't need (personal info, empty columns, etc.)
columns_to_remove = [
    "Product Description", "Customer Email", "Customer Password",
    "Customer Fname", "Customer Lname", "Customer Street",
    "Product Image", "Order Zipcode"
]
df = df.drop(columns=columns_to_remove, errors="ignore")

# Convert date columns from text to real dates
df["order date (DateOrders)"] = pd.to_datetime(df["order date (DateOrders)"])
df["shipping date (DateOrders)"] = pd.to_datetime(df["shipping date (DateOrders)"])

# Fill missing zipcodes with 0 (only a few rows are missing this)
df["Customer Zipcode"] = df["Customer Zipcode"].fillna(0)

# Remove duplicate rows if any exist
df = df.drop_duplicates()

print("\nData cleaned. New shape:", df.shape)


# ==========================================================
# STEP 3: CREATE NEW USEFUL COLUMNS (FEATURE ENGINEERING)
# ==========================================================

# Get the year and month name from the order date
df["Order Year"] = df["order date (DateOrders)"].dt.year
df["Order Month"] = df["order date (DateOrders)"].dt.strftime("%B")  # e.g. "January"

# Delivery delay = how many days late (or early) the order was
df["Delivery Delay"] = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]

# Mark an order as "canceled" if its status is CANCELED or SUSPECTED_FRAUD
df["Is Canceled"] = df["Order Status"].isin(["CANCELED", "SUSPECTED_FRAUD"])


# ==========================================================
# STEP 4: SALES PERFORMANCE ANALYSIS
# ==========================================================

# Total sales and profit for each product category
sales_by_category = df.groupby("Category Name")[["Sales", "Order Profit Per Order"]].sum()
sales_by_category = sales_by_category.sort_values("Sales", ascending=False)

print("\nTop 10 categories by sales:")
print(sales_by_category.head(10))

# Chart: Top 10 categories by sales
top10_categories = sales_by_category.head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=top10_categories["Sales"], y=top10_categories.index)
plt.title("Top 10 Categories by Sales")
plt.xlabel("Total Sales ($)")
plt.savefig("charts/01_top_categories.png", bbox_inches="tight")
plt.close()

# Total profit for each region
profit_by_region = df.groupby("Order Region")["Order Profit Per Order"].sum()
profit_by_region = profit_by_region.sort_values(ascending=False)

print("\nTop 5 regions by profit:")
print(profit_by_region.head(5))

# Chart: Profit by region
plt.figure(figsize=(12, 6))
sns.barplot(x=profit_by_region.index, y=profit_by_region.values)
plt.title("Profit by Region")
plt.xticks(rotation=75, ha="right")
plt.savefig("charts/02_profit_by_region.png", bbox_inches="tight")
plt.close()


# ==========================================================
# STEP 5: CUSTOMER SEGMENTATION
# ==========================================================

# Total amount spent by each customer
spending_by_customer = df.groupby("Customer Id")["Sales"].sum()
spending_by_customer = spending_by_customer.sort_values(ascending=False)

print("\nTop 10 customers by spending:")
print(spending_by_customer.head(10))

# How many orders each customer has placed
orders_per_customer = df.groupby("Customer Id")["Order Id"].nunique()

# Count how many customers placed 1 order, 2 orders, 3 orders, etc.
order_frequency = orders_per_customer.value_counts().sort_index()

# Chart: Order frequency distribution (pie chart)
plt.figure(figsize=(7, 7))
order_frequency.head(5).plot.pie(autopct="%1.0f%%", ylabel="")
plt.title("How Often Customers Order")
plt.savefig("charts/03_order_frequency.png", bbox_inches="tight")
plt.close()


# ==========================================================
# STEP 6: SHIPPING & DELIVERY ANALYSIS
# ==========================================================

# Count how many orders fall into each delivery status
delivery_status_count = df["Delivery Status"].value_counts()
print("\nDelivery status counts:")
print(delivery_status_count)

# Chart: Delivery status breakdown (pie chart)
plt.figure(figsize=(7, 7))
delivery_status_count.plot.pie(autopct="%1.1f%%", ylabel="")
plt.title("Delivery Status Breakdown")
plt.savefig("charts/04_delivery_status.png", bbox_inches="tight")
plt.close()

# Average delay for each shipping mode
delay_by_shipping_mode = df.groupby("Shipping Mode")["Delivery Delay"].mean()
print("\nAverage delay by shipping mode:")
print(delay_by_shipping_mode)


# ==========================================================
# STEP 7: PROFITABILITY ANALYSIS
# ==========================================================

# Most and least profitable categories
profit_sorted = sales_by_category.sort_values("Order Profit Per Order", ascending=False)
print("\nMost profitable category:", profit_sorted.index[0])
print("Least profitable category:", profit_sorted.index[-1])

# Top 10 most profitable products
profit_by_product = df.groupby("Product Name")["Order Profit Per Order"].sum()
profit_by_product = profit_by_product.sort_values(ascending=False)

print("\nTop 10 most profitable products:")
print(profit_by_product.head(10))

# Chart: Top 10 profitable products
plt.figure(figsize=(10, 6))
sns.barplot(x=profit_by_product.head(10).values, y=profit_by_product.head(10).index)
plt.title("Top 10 Most Profitable Products")
plt.xlabel("Total Profit ($)")
plt.savefig("charts/05_top_products.png", bbox_inches="tight")
plt.close()

# Does giving a discount affect profit? Check the correlation.
discount_profit_correlation = df["Order Item Discount Rate"].corr(df["Order Profit Per Order"])
print(f"\nCorrelation between discount rate and profit: {discount_profit_correlation:.3f}")


# ==========================================================
# STEP 8: ORDER TRENDS OVER TIME
# ==========================================================

# Total profit for each year
profit_by_year = df.groupby("Order Year")["Order Profit Per Order"].sum()
print("\nProfit by year:")
print(profit_by_year)

# Chart: Profit by year
plt.figure(figsize=(8, 6))
sns.barplot(x=profit_by_year.index, y=profit_by_year.values)
plt.title("Total Profit by Year")
plt.savefig("charts/06_profit_by_year.png", bbox_inches="tight")
plt.close()

# Number of orders placed in each month (across all years)
month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
orders_by_month = df.groupby("Order Month")["Order Id"].nunique().reindex(month_order)

# Chart: Orders by month
plt.figure(figsize=(10, 6))
orders_by_month.plot(kind="line", marker="o")
plt.title("Number of Orders by Month")
plt.xticks(rotation=45)
plt.savefig("charts/07_orders_by_month.png", bbox_inches="tight")
plt.close()


# ==========================================================
# STEP 9: RETURNS & CANCELLATIONS
# ==========================================================

# Count of each order status
order_status_count = df["Order Status"].value_counts()
print("\nOrder status counts:")
print(order_status_count)

# Percentage of orders that were canceled or flagged as fraud
cancellation_rate = df["Is Canceled"].mean() * 100
print(f"\nCancellation rate: {cancellation_rate:.2f}%")

# Chart: Order status breakdown
plt.figure(figsize=(9, 6))
sns.barplot(x=order_status_count.values, y=order_status_count.index)
plt.title("Order Status Breakdown")
plt.savefig("charts/08_order_status.png", bbox_inches="tight")
plt.close()


# ==========================================================
# STEP 10: SUMMARY OF KEY INSIGHTS
# ==========================================================

print("\n===== KEY INSIGHTS =====")
print(f"1. Top selling category: {sales_by_category.index[0]}")
print(f"2. Most profitable region: {profit_by_region.index[0]}")
print(f"3. Top customer ID: {spending_by_customer.index[0]}")
print(f"4. Most profitable product: {profit_by_product.index[0]}")
print(f"5. Discount vs profit correlation: {discount_profit_correlation:.2f} (very weak)")
print(f"6. Cancellation rate: {cancellation_rate:.2f}%")
print(f"7. Best year for profit: {profit_by_year.idxmax()}")
print(f"8. Busiest month for orders: {orders_by_month.idxmax()}")

print("\nAll charts saved in the 'charts' folder.")
