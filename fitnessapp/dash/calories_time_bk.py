from django.shortcuts import render
from fitnessapp.models import Workout, User
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now
from bokeh.plotting import figure
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource, CategoricalColorMapper
import pandas as pd
import json
from bokeh.palettes import Viridis256
from bokeh.transform import linear_cmap
from fitnessapp.queries.calories_time import get_workout_data


def prepare_workout_dataframe(data):
    df = pd.DataFrame(data)
    if df.empty:
        return None

    df['workout_time_begin'] = pd.to_datetime(df['workout_time_begin'], errors='coerce')
    df['user'] = df['user__username']

    df['duration'] = pd.to_numeric(df['duration'], errors='coerce')
    df['burned_calories'] = pd.to_numeric(df['burned_calories'], errors='coerce')

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

from bokeh.palettes import Category10
from bokeh.models import CategoricalColorMapper

def create_scatter_plot(df):
    if df is None or df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    users = df['user'].unique().tolist()

    if not users:
        return None, "<p>Не знайдено користувачів для відображення на графіку.</p>"

    num_users = len(users)

    if num_users > 10:
        palette = (Category10[10] * ((num_users // 10) + 1))[:num_users]
    else:
        palette = Category10[10][:num_users]

    color_map = CategoricalColorMapper(factors=users, palette=palette)
    source = ColumnDataSource(df)

    p = figure(title="Кореляція між тривалістю тренування та спаленими калоріями",
               x_axis_label='Тривалість тренування (години)',
               y_axis_label='Спалені калорії',
               height=400, width=700)

    p.scatter(x='duration', y='burned_calories', source=source, size=8, alpha=0.6, legend_field='user', color={'field': 'user', 'transform': color_map})

    p.legend.title = 'Користувач'
    p.legend.location = "top_left"

    chart_json = json_item(p)
    return chart_json, None


def scatter_plot_view_bk(request):
    start_date = request.GET.get('start_date', (now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))
    start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

    selected_user_id = request.GET.get('user', None)
    workout_data = get_workout_data(start_date, end_date, user_id=selected_user_id)
    data_frame = prepare_workout_dataframe(workout_data)

    scatter_chart, error_message = create_scatter_plot(data_frame)
    scatter_chart = json.dumps(scatter_chart) if scatter_chart else None

    statistics = calculate_statistics(data_frame)

    context = {
        'chart': scatter_chart,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'users': User.objects.all(),
        'selected_user': selected_user_id,
        'statistics': statistics,
        'data_table': workout_data,
    }

    return render(request, 'dashboard/calories_time_bk.html', context)
