from re import L
import pandas as pd
import numpy as np
import dash
from dash import dcc 
from dash import html
import plotly.graph_objects as go
import plotly.express as px

# Initializing colors & stylesheets
colors = ['hsl('+str(h)+',70%'+',70%)' for h in np.linspace(0, 360, 20)]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Importing csv
order_products_prior_df = pd.read_csv("instacart-market-basket-analysis/order_products__prior.csv")
orders_df = pd.read_csv("instacart-market-basket-analysis/orders.csv")
products_df = pd.read_csv("instacart-market-basket-analysis/products.csv")
aisles_df = pd.read_csv("instacart-market-basket-analysis/aisles.csv")
departments_df = pd.read_csv("instacart-market-basket-analysis/departments.csv")

# Merging Dataframes
order_products_prior_df = pd.merge(order_products_prior_df, products_df, on='product_id', how='left')
order_products_prior_df = pd.merge(order_products_prior_df, aisles_df, on='aisle_id', how='left')
order_products_prior_df = pd.merge(order_products_prior_df, departments_df, on='department_id', how='left')


# Plots ####################################################################################################################
def bar_max_order_num(orders_df):
    # Groupby user_id, take max order_number for each user_id (max num of orders for user_id)
    max_orders_each_user = orders_df.groupby("user_id")["order_number"].aggregate(np.max).reset_index()
    # Number of times all user orders
    order_number_count = max_orders_each_user.order_number.value_counts()

    bar_fig = go.Figure(data = [go.Bar(
        x = order_number_count.index,
        y = order_number_count.values,
    )],
    layout = dict(
        title = {'text': 'Number Of Occurrences For Maximum Order Of Customers'},
        xaxis = dict(
            title = 'Maximum Order Numbers',
            tickmode = 'linear'
        ),
        yaxis = { 'title': 'Number of Occurrences'}
    ))
    return bar_fig

def count_orders_day(orders_df):
    count_fig = go.Figure(data = [go.Bar(
        x = orders_df['order_dow'].value_counts(),
        marker_color = colors,
    )],
    layout = dict(
        title = {'text': 'Orders Made Per Day'},
        xaxis = { 'title': 'Number of Orders' },
        yaxis = { 'title': 'Day of Week'} 
    ))
    return count_fig

def heat_map_orders_day_hour(orders_df):
    # Combine the day of week and hour of day to see the distribution
    grouped_df = orders_df.groupby(["order_dow", "order_hour_of_day"])["order_number"].agg("count").reset_index()
    grouped_pivot_df = grouped_df.pivot('order_dow', 'order_hour_of_day', 'order_number')

    heat_fig = px.imshow(grouped_pivot_df,
        labels=dict(x="Hour Of Day", y="Day Of Week", color="Number Of Orders"),
        x=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'],
        y=['Sat', 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    )
    return heat_fig

def bar_top_aisle(order_products_prior_df):
    # Obtain top important aisles
    count_srs = order_products_prior_df['aisle'].value_counts().head(15)

    bar_fig = go.Figure(data = [go.Bar(
        x = count_srs.index,
        y = count_srs.values,
        marker_color = colors,
    )],
    layout = dict(
        title = {'text': 'Top 15 Popular Aisle'},
        xaxis = {'title': 'Aisle'},
        yaxis = { 'title': 'Number of Orders'}
    ))
    return bar_fig

def scatter_department_reorder_ratio(order_products_prior_df):
    # Reorder ratio of each department
    grouped_df = order_products_prior_df.groupby(["department"])["reordered"].agg("mean").reset_index()

    scatter_fig = go.Figure(data = [go.Scatter(
        x = grouped_df['department'].values,
        y = grouped_df['reordered'].values,
        mode='lines+markers'
    )],
    layout = dict(
        title = {'text': 'Department Reorder Ratio'},
        xaxis = {'title': 'Department'},
        yaxis = {'title': 'Reorder Ratio'}
    ))
    return scatter_fig


# App ####################################################################################################################

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.title = 'Market Basket Analysis'

app.layout = html.Div(children = [

    html.H2(style = {'textAlign': 'center', 'fontFamily': "Sans-Serif"},
    children = "Market Basket Analysis"),

    html.Div([ dcc.Graph(id = 'bar_max_order_num', figure = bar_max_order_num(orders_df)) ]),

    html.Div([
        html.Div([ dcc.Graph(id = 'count_orders_day', figure = count_orders_day(orders_df)) ], className = "six columns"),
        html.Div([ dcc.Graph(id = 'heat_map_orders_day_hour', figure = heat_map_orders_day_hour(orders_df)) ], className = "six columns")
    ], className = "row"),

    html.Div([ dcc.Graph(id = 'top_aisle', figure = bar_top_aisle(order_products_prior_df)) ]),

    html.Div([ dcc.Graph(id = 'scatter_department_reorder_ratio', figure = scatter_department_reorder_ratio(order_products_prior_df)) ]),

])

if __name__ == "__main__":
    app.run_server()