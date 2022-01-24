import os
import logging
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



assets_dir = "assets"
img_dir = "img"

df = pd.read_csv('workouts.csv')
# Dropping any rows with missing values for Workout Length and Calories Burned
df = df.dropna(axis=0, how='any', subset=['Length (minutes)', 'Calories Burned'])

logging.basicConfig(
    filename='app.log', 
    format='%(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
fav_instructor = df['Instructor Name'].mode()[0]


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

def get_cycling_class_length_chart(workout_df: pd.DataFrame) -> px.scatter:
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


def get_calories_burned_per_week_chart(workout_df: pd.DataFrame) -> px.scatter:
    for tz in ['EST', 'EDT', '-04', '-05']:
        workout_df['Workout Timestamp']= workout_df['Workout Timestamp'].str.replace(f"\({tz}\)", '')
    workout_df['Workout Timestamp'] = pd.to_datetime(workout_df['Workout Timestamp'], format='%Y-%m-%d %H:%M', errors='coerce')
    
    workout_df['Calories Burned'] = workout_df['Calories Burned'].fillna(0)
    workout_df['Total Output'] = workout_df['Total Output'].fillna(0)
    calories_df = workout_df.groupby(pd.Grouper(key='Workout Timestamp', freq='W'))['Calories Burned'].agg('sum').reset_index()
    total_output_df = workout_df.groupby(pd.Grouper(key='Workout Timestamp', freq='W'))['Total Output'].agg('sum').reset_index()
    line = make_subplots(specs=[[{"secondary_y": True}]])
    ts = calories_df['Workout Timestamp'].to_list()
    calories = calories_df['Calories Burned'].to_list()
    total_output = total_output_df['Total Output'].to_list()
    line.add_trace(go.Scatter(x=ts, y=calories,
                                marker=dict(size=10, color='MediumPurple'),
                                name='Total Calories'
                            ),
                            secondary_y=False
    )
    line.add_trace(go.Scatter(x=ts, y=total_output,
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
        width=1600
    )

    line.update_yaxes(title_text="Total Output", secondary_y=True)
    line.update_yaxes(title_text="Calories Burned", secondary_y=False)
    line.update_xaxes(title="Week")
    return line

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
            "width": "55rem",
            "margin-left": "1rem",
            "margin-top": "1rem",
            "margin-bottom": "1rem"
        }
    )

classLengthCard = dbc.Card([
    dbc.CardBody([
        html.Center(html.H1("Calories by Class Length", className='card-title')),
        dcc.Graph(
            id='class-length-by-calories-chart',
            figure=get_cycling_class_length_chart(df)
        )
    ])
],
    color='info',
    outline=True,
    style={
        "width": "55rem",
        "margin-left": "45rem",
        "margin-bottom": "1rem"
    }
)

instructorCard = dbc.Card([
    dbc.CardBody([
        html.Center(html.H1("Instructor by Fitness Discipline", className='card-title')),
        dcc.Graph(
            id='instructor-by-discipline-chart',
            figure=get_instructors_by_discipline_chart(df),
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
        "margin-bottom": "1rem"
    }
)

fitnessDisciplineCard = dbc.Card([
    dbc.CardBody([
        html.Center(html.H1("Fitness Discipline Breakdown", className='card-title')),
        html.P("This chart shows the percentage of time spent in minutes for each fitness discipline.", className='card-body'),
        dcc.Graph(
            id='fitness-discipline-by-calories-chart',
            figure=get_fitness_discipline_chart(df)
        )
    ])
],
    color='info',
    outline=True,
    style={
        "width": "55rem",
        "margin-left": "1rem",
        "margin-bottom": "1rem"
    }
)

weeklyCaloriesBurnedCard = dbc.Card([
    dbc.CardBody([
        html.Center(html.H1("Weekly Calorie and Output Breakdown", className='card-title')),
        dcc.Graph(
            id='weekly-calories-burned-chart',
            figure=get_calories_burned_per_week_chart(df)
        )
    ])
],
    outline=True,
    color='info',
    style={
        "width": "55rem",
        "margin-left": "1rem",
        "margin-bottom": "1rem"
    }
)

topInstructorCard = dbc.Card([
    dbc.CardBody([
        html.Center(html.H1("Top Instructor", className='card-title')),
        html.Center(html.H3(f"{fav_instructor} is the top instructor!")),
        get_top_instructor(df)
    ])
],
    outline=True,
    color='info',
    style={
        "width": "55rem",
        "margin-left": "45rem",
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
                    topInstructorCard,
                    classLengthCard,
                ]),
            dbc.Col([
                fitnessDisciplineCard,
                weeklyCaloriesBurnedCard
                ]),
            ],
            justify="around",
            style={
                'margin-left': '0.5rem'
            },
        ),
        dbc.Row([
            instructorCard,
            ],
            justify="center",
            style={
                'margin-left': '0.5rem'
            },
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)