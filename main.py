import dash
import os
import requests
import logging
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd

assets_dir = "assets"
peloton_csv = "workouts.csv"

df = pd.read_csv(peloton_csv)
df = df.dropna(axis=1, how='all')
logging.basicConfig(
    filename='app.log', 
    filemode='w', 
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
fav_instructor_name = df['Instructor Name'].mode()[0]
fav_instructor_image = os.path.join(
    assets_dir, 
    fav_instructor_name.lower().replace(" ", "_") + ".png"
)

app = Dash()

app.layout = html.Div(children=[
    html.H1('Favorite Instructor'),
    html.Img(src=fav_instructor_image),
    html.P(fav_instructor_name),
])

if __name__ == "__main__":
    app.run_server(debug=True)