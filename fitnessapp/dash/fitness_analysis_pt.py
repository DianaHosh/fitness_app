from django.shortcuts import render
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from fitnessapp.queries.fitness_analysis import get_workout_data
from fitnessapp.models import User

def prepare_dataframe(data, sort_order):
    df = pd.DataFrame(data)

    if not df.empty:
        df['user_with_index'] = df['username'].astype(str) + " #" + df.groupby('username').cumcount().astype(str)
        df['workout_start_time'] = pd.to_datetime(df['workout_start_time'])
        df['workout_end_time'] = pd.to_datetime(df['workout_end_time'])
        df['workout_duration_minutes'] = (df['workout_end_time'] - df['workout_start_time']).dt.total_seconds() / 60

        if sort_order == "asc":
            df = df.sort_values(by='workout_duration_minutes', ascending=True).reset_index(drop=True)
        elif sort_order == "desc":
            df = df.sort_values(by='workout_duration_minutes', ascending=False).reset_index(drop=True)

    return df

def calculate_statistics(df):
    if df.empty:
        return {
            'mean': 0,
            'median': 0,
            'min': 0,
            'max': 0
        }

    return {
        'min': round(df['workout_duration_minutes'].min(), 5),
        'max': round(df['workout_duration_minutes'].max(), 5),
        'mean': round(df['workout_duration_minutes'].mean(), 5),
        'median': round(df['workout_duration_minutes'].median(), 5),
    }

def create_plotly_chart(df):
    if df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    fig = px.bar(
        df,
        x='user_with_index',
        y='workout_duration_minutes',
        title="Аналіз тренувань",
        labels={
            "user_with_index": "Користувач",
            "workout_duration_minutes": "Тривалість тренувань (хв)"
        },
        color_discrete_sequence=["blue"]
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title="Користувач",
        yaxis_title="Тривалість тренувань (хв)",
        height=500,
        width=900,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graph_json

def workout_analysis_pt(request):
    sort_order = request.GET.get('sort', 'desc')
    selected_user = request.GET.get('user', '')

    users = User.objects.all()

    workout_data = get_workout_data()
    if selected_user:
        workout_data = workout_data.filter(user_id=selected_user)

    data = list(workout_data.values('user', 'workout_start_time', 'workout_end_time', 'username'))

    df_workout = prepare_dataframe(data, sort_order)
    stats = calculate_statistics(df_workout)
    chart = create_plotly_chart(df_workout)

    return render(request, 'dashboard/fitness_analysis_pt.html', {
        'chart': chart,
        'data_table': df_workout.to_dict(orient='records'),
        'stats': stats,
        'sort_order': sort_order,
        'users': users,
        'selected_user': str(selected_user),
    })