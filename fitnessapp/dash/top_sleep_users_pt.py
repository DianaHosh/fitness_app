from django.db.models import Sum, F, Value, DateField
from django.db.models.functions import Cast
from django.utils.timezone import now, make_aware
from datetime import timedelta, datetime
from django.shortcuts import render
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from fitnessapp.models import Sleep, User
from fitnessapp.queries.top_sleep_users import get_top_sleep_data

def prepare_sleep_dataframe(data):
    df = pd.DataFrame(data)

    if df.empty or 'user__username' not in df.columns:
        return None

    df.rename(columns={'user__username': 'user', 'total_sleep': 'total_sleep_hours'}, inplace=True)
    return df

def calculate_statistics(df):
    if df is None or df.empty:
        return {
            'min': None,
            'max': None,
            'mean': None,
            'median': None
        }

    return {
        'min': df['total_sleep_hours'].min(),
        'max': df['total_sleep_hours'].max(),
        'mean': df['total_sleep_hours'].mean(),
        'median': df['total_sleep_hours'].median()
    }

def create_sleep_chart(df):
    if df is None or df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    fig = px.bar(
        df,
        x='user',
        y='total_sleep_hours',
        title='Топ користувачів за тривалістю сну',
        labels={'user': 'Користувач', 'total_sleep_hours': 'Години сну'},
        text_auto=True
    )

    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder, ensure_ascii=False)

    return chart_json

def sleep_chart_view_pt(request):
    start_date = request.GET.get('start_date', (now() - timedelta(days=14)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))

    start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

    sleep_data = get_top_sleep_data(start_date, end_date)
    data_frame = prepare_sleep_dataframe(sleep_data)

    statistics = calculate_statistics(data_frame)
    chart = create_sleep_chart(data_frame)

    return render(request, 'dashboard/top_sleep_users_pt.html', {
        'chart': chart,
        'data_table': sleep_data,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'statistics': statistics
    })