from django.db.models import Sum, F, Value, DateField
from django.db.models.functions import Cast
from django.utils.timezone import now, make_aware
from datetime import timedelta, datetime
from django.shortcuts import render
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from fitnessapp.models import Workout, User
import numpy as np
from fitnessapp.queries.top_calorie_burners import get_daily_calories_data

def prepare_calories_dataframe(data, user_id=None):
    df = pd.DataFrame(data)

    if df.empty or 'day' not in df.columns:
        return None

    df['day'] = pd.to_datetime(df['day'], errors='coerce').dt.strftime('%Y-%m-%d')
    df = df.dropna(subset=['day'])

    if user_id is None:
        df = df.groupby(['day', 'user__username']).agg({'total_calories_burned': 'sum'}).reset_index()
        df['user'] = df['user__username']
    else:
        df['user'] = df['user__username']

    return df


def create_calories_chart(df):
    if df is None or df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    fig = px.line(
        df,
        x='day',
        y='total_calories_burned',
        color='user',
        title='Калорії, спалені за обраний період',
        labels={'day': 'Дата', 'total_calories_burned': 'Калорії'},
        markers=True
    )

    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)

    return chart_json


def calories_chart_view_pt(request):
    start_date = request.GET.get('start_date', (now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))

    start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

    selected_user_id = request.GET.get('user', None)

    calories_data = get_daily_calories_data(start_date, end_date, user_id=selected_user_id)
    data_frame = prepare_calories_dataframe(list(calories_data), user_id=selected_user_id)

    if data_frame is not None and not data_frame.empty:
        stats = {
            'min': round(data_frame['total_calories_burned'].min(), 5),
            'max': round(data_frame['total_calories_burned'].max(), 5),
            'mean': round(data_frame['total_calories_burned'].mean(), 5),
            'median': round(data_frame['total_calories_burned'].median(), 5),
        }
    else:
        stats = None

    chart = create_calories_chart(data_frame)

    return render(request, 'dashboard/top_calorie_burners_pt.html', {
        'chart': chart,
        'users': User.objects.all(),
        'selected_user': selected_user_id,
        'data_table': list(calories_data),
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'stats': stats,
    })

