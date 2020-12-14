# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 13:47:16 2020

@author: LIU_PAN
"""

import requests
import pandas as pd
import json
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


# http://makeup-api.herokuapp.com/
url='http://makeup-api.herokuapp.com/api/v1/products.json'

params={}

makeup_req=requests.get(url, params=params)
makeup_req.raise_for_status()

makeup=makeup_req.json()

GBP_TO_USD=1.33
CAD_TO_USD=0.79
# create list for each keys
id_number=[i['id'] for i in makeup]
brand=[i['brand'] for i in makeup]
name=[i['name'] for i in makeup]
price=[i['price'] for i in makeup]
currency=[i['currency'] for i in makeup]
image_link=[i['image_link'] for i in makeup]
product_link=[i['product_link'] for i in makeup]
website_link=[i['website_link'] for i in makeup]
description=[i['description'] for i in makeup]
rating=[i['rating'] for i in makeup]
category=[i['category'] for i in makeup]
product_type=[i['product_type'] for i in makeup]
tag_list=[i['tag_list'] for i in makeup]
# separate the color id and name from the product color list of dictionary
product_colors=[i['product_colors'] for i in makeup]
product_color_id=[]
product_color_name=[]
for i in product_colors:
    list_id=[]
    list_name=[]
    for n in i:
        list_id.append(n['hex_value'])
        list_name.append(n['colour_name'])
    product_color_id.append(list_id)
    product_color_name.append(list_name)
    
# create a dataframe from the list
df=pd.DataFrame(index=id_number)
df["ID"]=id_number
df["Brand"]=brand
df["Name"]=name
df["Price"]=price
df["Currency"]=currency
df["Image Link"]=image_link
df["Product Link"]=product_link
df["Website Link"]=website_link
df["Description"]=description
df["Rating"]=rating
df["Category"]=category
df["Product Type"]=product_type
df["Tag List"]=tag_list
df["Product Colors ID"]=product_color_id
df["Product Colors Name"]=product_color_name

# get rid of null in Brand and Price columns
df=df[df['Brand'].notnull()&df['Price'].notnull()]

# change all price to US dollars
df["Rating"]=df['Rating'].astype(float)
df["Price"]=df['Price'].astype(float)
df.loc[ df['Currency']=="CAD" , 'Price'] = df["Price"]*CAD_TO_USD
df.loc[ df['Currency']=="GBP" , 'Price'] = df["Price"]*GBP_TO_USD

# remove None in the brand and product lists and brand column in the dataframe
brand_name_list=set([i for i in brand if i])
product_type_list=set([i for i in product_type if i])

# dashboard
stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#Get a df for the plot of differenr brands and product types
df_plot=df[['Brand', 'Price','Product Type' ]]
df_plot=df_plot.groupby(['Brand', 'Product Type'])['Price'].mean()
brand_data, type_data = list(zip(*df_plot.index))
df2 = pd.DataFrame({'Brand' : brand_data, 'Product Type' : type_data})
df2['avg_price'] = df_plot.values

# generate table
def generate_table(df):
    df=df[["Brand","Name","Price","Product Link", "Description","Rating", "Product Type" ]]
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in df.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(len(df))
        ])
    ])

app = dash.Dash(__name__, external_stylesheets=stylesheet)

server = app.server

app.layout = html.Div([
    html.H1('Makeup Dashboard!', style={'textAlign': 'center'}),
    html.Div([html.H4('Price of Each Brand by Product Type'),
              dcc.Checklist(options=[{'label': 'blush', 'value': 'blush'},
                                     {'label': 'bronzer', 'value': 'bronzer'},
                                     {'label': 'eyebrow', 'value': 'eyebrow'},
                                     {'label': 'eyeliner', 'value': 'eyeliner'},
                                     {'label': 'eyeshadow', 'value': 'eyeshadow'},
                                     {'label': 'eoundation', 'value': 'foundation'},
                                     {'label': 'eip_liner', 'value': 'lip_liner'},
                                     {'label': 'lipstick', 'value': 'lipstick'},
                                     {'label': 'mascara', 'value': 'mascara'},
                                     {'label': 'nail_polish', 'value': 'nail_polish'}],
                           id="product_select_checklist",
                           value=[ 'eyeliner']),
              html.H4('Select Product Type to Display:'),
              dcc.Graph(id='fig'),
              html.H4('Select Rating to Display:'),
              dcc.RangeSlider(id='my-range-slider',
                              min=0,
                              max=5,
                              step=0.1,
                              value=[4.5,5]),
              html.Div(id="range_output"),
              html.H4('Select Brand Type to Display'),
              dcc.Dropdown(options=[{'label': 'almay', 'value': 'almay'},
                                   {'label': 'alva', 'value': 'alva'},
                                   {'label': 'anna sui', 'value': 'anna sui'},
                                   {'label': 'annabelle', 'value': 'annabelle'},
                                   {'label': 'benefit', 'value': 'benefit'},
                                   {'label': 'boosh', 'value': 'boosh'},
                                   {'label': 'burt\'s bees', 'value': 'burt\'s bees'},
                                   {'label': 'butter london', 'value': 'butter london'},
                                   {'label': 'c\'est moi', 'value': 'c\'est moi'},
                                   {'label': 'cargo cosmetics', 'value': 'cargo cosmetics'},
                                   {'label': 'china glaze', 'value': 'china glaze'},
                                   {'label': 'clinique', 'value': 'clinique'},
                                   {'label': 'coastal classic creation', 'value': 'coastal classic creation'},
                                   {'label': 'colourpop', 'value': 'colourpop'},
                                   {'label': 'covergirl', 'value': 'covergirl'},
                                   {'label': 'dalish', 'value': 'dalish'},
                                   {'label': 'deciem', 'value': 'deciem'},
                                   {'label': 'dior', 'value': 'dior'},
                                   {'label': 'dr. hauschka', 'value': 'dr. hauschka'},
                                   {'label': 'e.l.f.', 'value': 'e.l.f.'},
                                   {'label': 'essie', 'value': 'essie'},
                                   {'label': 'fenty', 'value': 'fenty'},
                                   {'label': 'glossier', 'value': 'glossier'},
                                   {'label': 'green people', 'value': 'green people'},
                                   {'label': 'iman', 'value': 'iman'},
                                   {'label': 'l\'oreal', 'value': 'l\'oreal'},
                                   {'label': 'lotus cosmetics usa', 'value': 'lotus cosmetics usa'},
                                   {'label': 'maia\'s mineral galaxy', 'value': 'maia\'s mineral galaxy'},
                                   {'label': 'marcelle', 'value': 'marcelle'},
                                   {'label': 'marienatie', 'value': 'marienatie'},
                                   {'label': 'maybelline', 'value': 'maybelline'},
                                   {'label': 'milani', 'value': 'milani'},
                                   {'label': 'mineral fusion', 'value': 'mineral fusion'},
                                   {'label': 'misa', 'value': 'misa'},
                                   {'label': 'mistura', 'value': 'mistura'},
                                   {'label': 'moov', 'value': 'moov'},
                                   {'label': 'nudus', 'value': 'nudus'},
                                   {'label': 'nyx', 'value': 'nyx'},
                                   {'label': 'orly', 'value': 'orly'},
                                   {'label': 'pacifica', 'value': 'pacifica'},
                                   {'label': 'penny lane organics', 'value': 'penny lane organics'},
                                   {'label': 'physicians formula', 'value': 'physicians formula'},
                                   {'label': 'piggy paint', 'value': 'piggy paint'},
                                   {'label': 'pure anada', 'value': 'pure anada'},
                                   {'label': 'rejuva minerals', 'value': 'rejuva minerals'},
                                   {'label': 'revlon', 'value': 'revlon'},
                                   {'label': 'sally b\'s skin yummies', 'value': 'sally b\'s skin yummies'},
                                   {'label': 'salon perfect', 'value': 'salon perfect'},
                                   {'label': 'sante', 'value': 'sante'},
                                   {'label': 'sinful colours', 'value': 'sinful colours'},
                                   {'label': 'smashbox', 'value': 'smashbox'},
                                   {'label': 'stila', 'value': 'stila'},
                                   {'label': 'suncoat', 'value': 'suncoat'},
                                   {'label': 'w3llpeople', 'value': 'w3llpeople'},
                                   {'label': 'wet n wild', 'value': 'wet n wild'},
                                   {'label': 'zorah', 'value': 'zorah'},
                                   {'label': 'zorah biocosmetiques', 'value': 'zorah biocosmetiques'}],
                          multi=True,
                          id='product_brand_dropdown', 
                          value=['annabelle','maybelline']),
             html.H4('Sort table by:'),
             dcc.Dropdown(options=[{'label': 'Brand', 'value': 'Brand'},
                                   {'label': 'Product Type', 'value': 'Product Type'},
                                   {'label': 'Price', 'value': 'Price'},
                                   {'label': 'Rating', 'value': 'Rating'}],
                          id='sort_by_dropdown', 
                          value='Price')],
             style={'width': '49%', 'display': 'inline-block'}),
    html.Div([dcc.Markdown(id='df_head'),
             html.Div(id="df_div")],
             style={'width': '49%', 'display': 'inline-block', 'float': 'right'})
    
    ])

# call back the table display and table heading on the right side of the browser and rating explained on the left side
@app.callback(
    [Output(component_id='df_head', component_property='children'),
     Output(component_id='df_div', component_property='children'),
     Output(component_id='range_output', component_property='children')],
    [Input(component_id='product_select_checklist', component_property='value'),
     Input(component_id='product_brand_dropdown', component_property='value'),
     Input(component_id='sort_by_dropdown', component_property='value'),
     Input(component_id='my-range-slider', component_property='value')]
)
def update_table(prduct_type_display, brand_to_display, sort_by, range_to_display):
    array_range=np.arange(range_to_display[0],range_to_display[1]+0.1,0.1)
    list_of_range=[round(i,2)for i in array_range.tolist()]
    x = df[df['Product Type'].isin(prduct_type_display) & df.Brand.isin(brand_to_display)& df.Rating.isin(list_of_range)].sort_values(sort_by)
    product_string=",".join(prduct_type_display)
    brand_string=",".join(brand_to_display)
    heading=f'The Table Displayed Product Type: {product_string} in Brand: {brand_string} for the Rating from {range_to_display[0]} to {range_to_display[-1]}, Sorted by {sort_by} '
    rating_out=f"You Select Product for Rating from {range_to_display[0]} to {range_to_display[-1]} "
    return heading, generate_table(x),rating_out

#call back the graph
@app.callback(
    Output(component_id='fig', component_property='figure'),
    [Input(component_id='product_select_checklist', component_property='value')])
def graph_df(product_selected):
    y=df2.loc[df2['Product Type'].isin (product_selected)]
    fig = px.bar(y, x="Brand", y="avg_price", color="Product Type", barmode="group")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

