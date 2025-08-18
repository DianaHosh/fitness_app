import plotly.express as px
import pandas as pd
from django.shortcuts import render
from fitnessapp.models import Workout
from datetime import datetime
from django.utils.timezone import make_aware, now
from datetime import timedelta
from fitnessapp.models import Workout, User
from fitnessapp.queries.calories_time import get_workout_data

def prepare_workout_dataframe(data):
    df = pd.DataFrame(data)
    if df.empty:
        return None

    df['workout_time_begin'] = pd.to_datetime(df['workout_time_begin'], errors='coerce')
    df['user'] = df['user__username']

    return df

def calculate_statistics(df):
    if df is None or df.empty:
        return {}

    statistics = {
        'duration_mean': round(df['duration'].mean(), 5),
        'duration_median': round(df['duration'].median(), 5),
        'duration_min': round(df['duration'].min(), 5),
        'duration_max': round(df['duration'].max(), 5),
        'burned_calories_mean': round(df['burned_calories'].mean(), 5),
        'burned_calories_median': round(df['burned_calories'].median(), 5),
        'burned_calories_min': round(df['burned_calories'].min(), 5),
        'burned_calories_max': round(df['burned_calories'].max(), 5),
    }

    return statistics

def create_scatter_plot(df):
    if df is None or df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    fig = px.scatter(
        df,
        x='duration',
        y='burned_calories',
        color='user',
        title='Кореляція між тривалістю тренування та спаленими калоріями',
        labels={'duration': 'Тривалість тренування (години)', 'burned_calories': 'Спалені калорії'},
        hover_data=['user', 'workout_time_begin']
    )

    return fig.to_json()

def scatter_plot_view_pt(request):
    start_date = request.GET.get('start_date', (now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))

    start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

    selected_user_id = request.GET.get('user', None)

    workout_data = get_workout_data(start_date, end_date, user_id=selected_user_id)
    data_frame = prepare_workout_dataframe(workout_data)
    scatter_chart = create_scatter_plot(data_frame)

    statistics = calculate_statistics(data_frame)

    return render(request, 'dashboard/calories_time_pt.html', {
        'chart': scatter_chart,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'users': User.objects.all(),
        'selected_user': selected_user_id,
        'statistics': statistics,
        'data_table': workout_data
    })
