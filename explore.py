# https://www.kaggle.com/sudalairajkumar/simple-exploration-notebook-instacart

"""
Try and explore the basic information about the dataset given. The goal of the competition is to predict which products will be in a user's next order.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

color = sns.color_palette()
pd.options.mode.chained_assignment = None
pd.options.display.max_columns = 10


"""
Read all the files.
"""
order_products_train_df = pd.read_csv("instacart-market-basket-analysis/order_products__train.csv")
order_products_prior_df = pd.read_csv("instacart-market-basket-analysis/order_products__prior.csv")
orders_df = pd.read_csv("instacart-market-basket-analysis/orders.csv")
products_df = pd.read_csv("instacart-market-basket-analysis/products.csv")
aisles_df = pd.read_csv("instacart-market-basket-analysis/aisles.csv")
departments_df = pd.read_csv("instacart-market-basket-analysis/departments.csv")

print(orders_df.head(5))
print(orders_df.tail(5))


"""
eval_set column here specifies which of the 3 dataset (prior, train or test) the given row goes to.
"""
print(f"orders columns: {list(orders_df.columns.values)} \n")


"""
In this dataset, 4 to 100 orders of a customer are given, will need to predict the products that will be re-ordered.
So, the last order of the customer has been taken out and divided into train and test sets.
Prior order informations are in 'order_products_prior_df'.
"""
print(f"order_products_prior columns: {list(order_products_prior_df.columns.values)} \n")
print(f"order_products_train_df columns: {list(order_products_train_df.columns.values)} \n")


"""
Let's get the count of rows in each of the 3 sets.
Series: Only contain single list with index.
Dataframe: Can be made of more than 1 series, a collection of series that can be used to analyse the data.
"""
print(orders_df.eval_set)
print(orders_df.loc[:,'eval_set'])

## This is a series
count_of_rows = orders_df.eval_set.value_counts(ascending=True)
print(count_of_rows)

plt.figure(figsize=(12, 8))
sns.barplot(count_of_rows.index, count_of_rows.values, alpha=0.8, color=color[1])

plt.ylabel('Number of Occurrences', fontsize = 12)
plt.xlabel('Eval set type', fontsize = 12)
plt.title('Count of rows in each dataset', fontsize = 15)
plt.xticks(rotation = 'vertical')
plt.show()


"""
There are 206,209 customers in total.
The last purchase of 131,209 customers are given as the train set.
We need to predict for the rest 75,000 customers.
"""
def get_unique_count(x):
    return len(np.unique(x))

unique_count_of_customers = orders_df.groupby("eval_set")["user_id"].aggregate(get_unique_count)

print(orders_df.groupby("eval_set").first())
print(orders_df.groupby("eval_set")["user_id"])
print(unique_count_of_customers)


"""
Now let us validate the claim that 4 to 100 orders of a customer are given.
"""
## Groupby user_id, take max order_number for each user_id (max num of orders for user_id)
max_orders_each_user = orders_df.groupby("user_id")["order_number"].aggregate(np.max).reset_index()

## Number of times all user orders
order_number_count = max_orders_each_user.order_number.value_counts()

plt.figure(figsize=(12,8))
sns.barplot(order_number_count.index, order_number_count.values, alpha=0.8, color=color[2])

plt.ylabel('Number of occurrences:', fontsize=12)
plt.xlabel('Max order number', fontsize=12)
plt.xticks(rotation='vertical')
plt.show()

print(orders_df.head(10))
print('\n', orders_df.groupby("user_id")["order_number"].agg(np.max))
print('\n', order_number_count.order_number.value_counts())


"""
See how the ordering habit changes with day of week.
0 = Saturday
1 = Sunday
..
"""
plt.figure(figsize=(12,8))
sns.countplot(x="order_dow", data=orders_df, color=color[0])

plt.ylabel('Count', fontsize=12)
plt.xlabel('Day of week', fontsize=12)
plt.xticks(rotation='vertical')
plt.title('Frequency of order by week day', fontsize=15)
plt.show()


"""
See how the distribution is w.r.t. time of the day.
So most orders are done through the day.
"""
plt.figure(figsize=(12,8))
sns.countplot(x="order_hour_of_day", data=orders_df, color=color[1])

plt.ylabel('Count', fontsize=12)
plt.xlabel('Hour of day', fontsize=12)
plt.xticks(rotation='vertical')
plt.title('Frequency of order by hour of day', fontsize=15)
plt.show()


"""
Combine the day of week and hour of day to see the distribution.
Seems like Saturday evenings and Sunday mornings are the prime time for orders.
"""
grouped_df = orders_df.groupby(["order_dow", "order_hour_of_day"])["order_number"].agg("count").reset_index()
print(orders_df[["order_dow", "order_hour_of_day", "order_number"]].groupby(["order_dow", "order_hour_of_day"]).agg("count").reset_index())
print(f"grouped_order_num: \n {grouped_df}")

grouped_pivot_df = grouped_df.pivot('order_dow', 'order_hour_of_day', 'order_number')
print(f"pivot: \n {grouped_pivot_df}")

plt.figure(figsize=(12, 6))
sns.heatmap(grouped_pivot_df)
plt.title("Frequency of Day of week vs Hour of day")
plt.show()


"""
Now let's check the time interval between the orders.
"""
plt.figure(figsize=(12,8))
sns.countplot(x="days_since_prior_order", data=orders_df, color=color[3])

plt.ylabel('Count', fontsize=12)
plt.xlabel('Days since prior order', fontsize=12)
plt.xticks(rotation='vertical')
plt.title('Frequency distribution by days since prior order', fontsize=15)
plt.show()