import os
import base64
import datetime
import io

import logging
from dash.dependencies import Input, Output, State
from dash import Dash, dcc, html, callback, dash_table
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px



assets_dir = "assets"
img_dir = "img"

df = pd.read_csv('workouts.csv')
# Dropping any rows with missing values for Workout Length and Calories Burned
df = df.dropna(axis=0, how='any', subset=['Length (minutes)', 'Calories Burned'])

# Getting the most frequent Instructor Name in the data and fetching that image
fav_instructor_name = df['Instructor Name'].mode()[0]
fav_instructor_image = os.path.join(
    assets_dir, 
    img_dir, 
    fav_instructor_name.lower().replace(" ", "_") + ".png"
)
instructors_output = df.loc[:,['Instructor Name', 'Total Output']]

logging.basicConfig(
    filename='app.log', 
    encoding='utf-8', 
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

app = Dash()
df['Length (minutes)'] = pd.to_numeric(df['Length (minutes)'], errors='coerce')
df['Title'] = df['Title'].to_string(index=False)

fig = px.scatter(
    df[df['Fitness Discipline'] == 'Cycling'], 
    x="Length (minutes)", 
    y="Calories Burned", 
    color="Calories Burned", 
    size="Total Output",
    title='Calories Burned by Class Length',
    hover_data=["Workout Timestamp","Instructor Name", "Fitness Discipline", "Length (minutes)", "Calories Burned", "Total Output"]
)
fig2 = px.pie(df, values="Length (minutes)", names="Fitness Discipline", title="Time broken down by Fitness Discipline")
fig3 = px.bar(df[['Instructor Name', 'Fitness Discipline']], x="Instructor Name", color="Fitness Discipline", title="Total Output by Instructor")
print(df.dtypes)
workouts_df = df[['Workout Timestamp', 'Calories Burned']]
workouts_df['Workout Timestamp'] = workouts_df['Workout Timestamp'].str.replace('\(EST\)', '')
workouts_df['Workout Timestamp'] = workouts_df['Workout Timestamp'].str.replace('\(-04\)', '')
workouts_df['Workout Timestamp'] = workouts_df['Workout Timestamp'].str.replace('\(-05\)', '')


workouts_df['Workout Timestamp'] = pd.to_datetime(workouts_df['Workout Timestamp'], format='%Y-%m-%d %H:%M', errors='coerce').fillna(pd.to_datetime(workouts_df['Workout Timestamp'], format='%Y-%m-%d %H:%M', errors='coerce'))
workouts_df.set_index('Workout Timestamp')
workouts_df = workouts_df.groupby(pd.Grouper(key="Workout Timestamp", freq='W'))['Calories Burned'].sum()
fig4 = px.line(workouts_df, y="Calories Burned", title="Total Calories Burned by Week")

app.layout = html.Div(
    [
        html.H1('Peloton Fitness Workout Tracker'),
        html.H2('Top Instructor across your Dataset'),
        html.Img(
            className="circular-square",
            src=fav_instructor_image
        ),
        html.H2('Calories Burned by Class Length'),
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig2),
        dcc.Graph(figure=fig3),
        dcc.Graph(figure=fig4),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)