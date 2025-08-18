from django.shortcuts import render
from fitnessapp.models import Workout, User
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now
from bokeh.plotting import figure
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource
from django.db.models import Sum, DateField
from django.db.models.functions import Cast
import json
import pandas as pd
from bokeh.palettes import Category20
from fitnessapp.queries.top_calorie_burners import get_daily_calories_data

def prepare_daily_dataframe(data):
    df = pd.DataFrame(data)
    if df.empty:
        return None

    df['day'] = pd.to_datetime(df['day'])
    df['total_calories_burned'] = pd.to_numeric(df['total_calories_burned'], errors='coerce')
    df['user'] = df['user__username']
    return df

def calculate_statistics(df):
    if df is None or df.empty:
        return None

    return {
        'burned_calories_mean': round(df['total_calories_burned'].mean(), 5),
        'burned_calories_median': round(df['total_calories_burned'].median(), 5),
        'burned_calories_min': round(df['total_calories_burned'].min(), 5),
        'burned_calories_max': round(df['total_calories_burned'].max(), 5),
    }

def create_line_chart(df, user_id):
    if df is None or df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    p = figure(title="Графік спалених калорій",
               x_axis_label='Дата',
               y_axis_label='Спалені калорії',
               x_axis_type='datetime',
               height=400, width=700)

    users = df['user'].unique()
    colors = Category20[20]

    for i, user in enumerate(users):
        user_data = df[df['user'] == user]
        source = ColumnDataSource(user_data)
        p.line(x='day', y='total_calories_burned', source=source, line_width=2, color=colors[i % 20], legend_label=user)

    p.legend.title = "Користувачі"
    p.legend.location = "top_left"

    chart_json = json_item(p)
    return chart_json, None

def calories_chart_view_bk(request):
    start_date = request.GET.get('start_date', (now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))
    start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

    selected_user_id = request.GET.get('user', None)
    workout_data = get_daily_calories_data(start_date, end_date, user_id=selected_user_id)
    data_frame = prepare_daily_dataframe(workout_data)

    statistics = calculate_statistics(data_frame)

    line_chart, error_message = create_line_chart(data_frame, selected_user_id)
    line_chart = json.dumps(line_chart) if line_chart else None

    context = {
        'chart': line_chart,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'users': User.objects.all(),
        'selected_user': selected_user_id,
        'data_table': workout_data,
        'statistics': statistics,
        'error_message': error_message,
    }

    return render(request, 'dashboard/top_calorie_burners_bk.html', context)
