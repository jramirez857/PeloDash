import os
import logging
import base64
import io
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
import dash_table


assets_dir = "assets"
img_dir = "img"

logging.basicConfig(
    filename='app.log', 
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

df = pd.read_csv("/home/jose/VSCodeProjects/PeloDash/workouts.csv")

def get_fitness_discipline_chart(workout_df: pd.DataFrame) -> px.scatter:
    pie = px.pie(
        workout_df,
        values="Length (minutes)",
        names="Fitness Discipline",
        title="Time Spent Per Fitness Discipline",
        hole=0.2,
    )
    pie.update_traces(textposition='inside', textinfo='percent+label')
    pie.update_layout(width=1600)
    pie.update_layout(title_x=0.5)
    return pie

def get_instructors_by_discipline_chart(workout_df: pd.DataFrame) -> px.bar:
    workout_df['count'] = workout_df['Workout Timestamp']
    workout_df = workout_df.groupby(['Instructor Name','Fitness Discipline'])['count'].agg('count').reset_index()
    chart = px.bar(workout_df, x="Instructor Name", y="count", color="Fitness Discipline", title="Total Output by Instructor", width=1600)
    chart.update_layout(
        title_x=0.5
    )
    return chart

def get_cycling_class_length_chart(start_date: datetime, end_time: datetime) -> px.scatter:
    workout_df = df.loc[(df['Workout Timestamp'] >= start_date) & (df['Workout Timestamp'] <= end_time)]
    length_by_calories_df = workout_df.dropna(axis='rows', how='any', subset=['Length (minutes)']).reset_index(drop=True)
    length_by_calories_df = length_by_calories_df.loc[length_by_calories_df['Fitness Discipline'] == 'Cycling']
    bx= px.box(
        length_by_calories_df,
        x="Length (minutes)",
        y="Calories Burned",
        title='Calories Burned by Cycling Class Length',
        hover_data=["Workout Timestamp","Instructor Name", "Fitness Discipline", "Length (minutes)", "Calories Burned", "Total Output"]
    )

    bx.update_layout(
        title_x=0.5
    )
    return bx

def get_top_instructor(workout_df: pd.DataFrame) -> px.bar:
    fav_instructor_name = workout_df['Instructor Name'].mode()[0]
    fav_instructor_image = os.path.join(
        assets_dir, 
        img_dir, 
        fav_instructor_name.lower().replace(" ", "_") + ".png"
    )
    return html.Center(
        html.Img(
        className="circular-square",
        src=fav_instructor_image,
        title=f"Favorite Instructor: {fav_instructor_name}",
        ),
    )
    

titleCard = dbc.Card([
        dbc.CardBody([
            html.H1("Welcome to your workout dashboard, Jose!", className='card-title'),
            ])
        ],
        color='dark',
        inverse=True,
        style={
            "width": "40rem",
            "margin-left": "1rem",
            "margin-top": "1rem",
            "margin-bottom": "1rem"
        }
    )

def create_class_length_card(workout_df: pd.DataFrame) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Center(html.H1("Calories by Class Length", className='card-title')),
            html.Center(
                dcc.DatePickerRange(
                    id='date-range-picker',
                    min_date_allowed=workout_df['Workout Timestamp'].min(),
                    max_date_allowed=workout_df['Workout Timestamp'].max(),
                    initial_visible_month=workout_df['Workout Timestamp'].min(),
                    start_date=workout_df['Workout Timestamp'].min(),
                    end_date=workout_df['Workout Timestamp'].max(),
                    style={
                        "margin-top": "1rem",
                        "margin-bottom": "1rem"
                    }
                ),
            ),
            dcc.Graph(
                id='class-length-by-calories-chart'        
            )
        ])
    ],
        color='info',
        outline=True,
        style={
            "width": "40rem",
            "margin-left": "5rem",
            "margin-bottom": "1rem"
        }
    )

def create_instructor_card(workout_df: pd.DataFrame) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Center(html.H1("Instructor by Fitness Discipline", className='card-title')),
            dcc.Graph(
                id='instructor-by-discipline-chart',
                figure=get_instructors_by_discipline_chart(workout_df),
                style={
                    "margin-top": "1rem",
                    "margin-bottom": "1rem"
                }
            )
        ])
    ],
        color='info',
        outline=True,
        style={
            "margin-top": "1rem",
            "margin-left": "1rem",
            "margin-bottom": "1rem"
        }
    )

def create_discipline_card(workout_df: pd.DataFrame) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Center(html.H1("Fitness Discipline Breakdown", className='card-title')),
            html.P("This chart shows the percentage of time spent in minutes for each fitness discipline.", className='card-body'),
            dcc.Graph(
                id='fitness-discipline-by-calories-chart',
                figure=get_fitness_discipline_chart(workout_df)
            )
        ])
    ],
        color='info',
        outline=True,
        style={
            "width": "40rem",
            "margin-left": "1rem",
            "margin-bottom": "1rem"
        }
    )


def create_top_instructor_card(workout_df: pd.DataFrame) -> dbc.Card:
    fav_instructor_name = workout_df['Instructor Name'].mode()[0]
    return dbc.Card([
        dbc.CardBody([
            html.Center(html.H1("Top Instructor", className='card-title')),
            html.Center(html.H3(f"{fav_instructor_name} is the top instructor!")),
            get_top_instructor(workout_df)
        ])
    ],
        outline=True,
        color='info',
        style={
            "width": "40rem",
            "margin-left": "5rem",
            "margin-bottom": "1rem"
        }
    )

def create_calories_card(workout_df: pd.DataFrame) -> dbc.Card:
    return dbc.Card([
        dbc.CardBody([
            html.Center(html.H1("Weekly Calorie and Output Breakdown", className='card-title')),
            html.Center(
                dcc.DatePickerRange(
                    id='date-range-picker-2',
                    min_date_allowed=workout_df['Workout Timestamp'].min(),
                    max_date_allowed=workout_df['Workout Timestamp'].max(),
                    initial_visible_month=workout_df['Workout Timestamp'].min(),
                    start_date=workout_df['Workout Timestamp'].min(),
                    end_date=workout_df['Workout Timestamp'].max(),
                    style={
                        "margin-top": "1rem",
                        "margin-bottom": "1rem"
                    }
                )
            ),
            dcc.Graph(
                id='weekly-calories-burned-chart'
            )
        ])
    ],
        outline=True,
        color='info',
        style={
            "width": "40rem",
            "margin-left": "1rem",
            "margin-bottom": "1rem"
        }
    )


app.layout = html.Div(
    children=[
        dbc.Row([
                html.Center(titleCard),
                ],
                justify="center",
                style={
                    'margin-left': '0.5rem'
                }
        ),
        dbc.Row([
            dbc.Col([
                create_top_instructor_card(df),
                create_class_length_card(df),
            ]),
            dbc.Col([
                create_calories_card(df),
                create_discipline_card(df)
            ])
        ]),
        dbc.Row([
            dbc.Col([
                create_instructor_card(df)
            ])
        ])
    ]
)



@app.callback(
    Output('class-length-by-calories-chart', 'figure'),
    [Input('date-range-picker', 'start_date'),
        Input('date-range-picker', 'end_date')]
)
def update_class_length_chart(start_date, end_date):
    return get_cycling_class_length_chart(start_date, end_date)


@app.callback(
    Output('weekly-calories-burned-chart', 'figure'),
    [   Input('date-range-picker-2', 'start_date'),
        Input('date-range-picker-2', 'end_date')]
)
def update_weekly_calories_burned_chart(start_date, end_date):
    dff = df.loc[(df['Workout Timestamp'] >= start_date) & (df['Workout Timestamp'] <= end_date)]
    for tz in ['EST', 'EDT', '-04', '-05']:
        dff['Workout Timestamp']= dff['Workout Timestamp'].str.replace(f"\({tz}\)", '')
    dff['Workout Timestamp'] = pd.to_datetime(dff['Workout Timestamp'], format='%Y-%m-%d %H:%M', errors='coerce')
    calories_df = dff.groupby(pd.Grouper(key='Workout Timestamp', freq='W'))['Calories Burned', 'Total Output'].agg('sum').reset_index()
    line = make_subplots(specs=[[{"secondary_y": True}]])
    line.add_trace(go.Scatter(x=calories_df['Workout Timestamp'], y=calories_df['Calories Burned'],
                                marker=dict(size=10, color='MediumPurple'),
                                name='Total Calories'
                            ),
                            secondary_y=False
    )
    line.add_trace(go.Scatter(x=calories_df['Workout Timestamp'], y=calories_df['Total Output'],
                                marker=dict(size=10, color='MediumSeaGreen'),
                                name='Total Output'
                            ),
                    secondary_y=True
    )

    line.update_layout(
        title="Calories and Total Output per Week",
        title_x=0.5,
        xaxis_title="Week",
        yaxis_title="Calories Burned",
    )

    line.update_yaxes(title_text="Total Output", secondary_y=True)
    line.update_yaxes(title_text="Calories Burned", secondary_y=False)
    line.update_xaxes(title="Week")
    return line

if __name__ == "__main__":
    app.run_server(debug=True)