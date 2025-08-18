from django.shortcuts import render
from django.db.models import Sum, F, Value
from django.db.models.functions import TruncDate, Cast
from django.utils.timezone import now
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
import json
from fitnessapp.models import User
from fitnessapp.queries.water_intake_per_weekday import get_water_intake_data

def prepare_water_intake_dataframe(data, user_id=None):
    df = pd.DataFrame(data)

    if 'day' not in df.columns:
        return None

    df['day'] = pd.to_datetime(df['day'], errors='coerce').dt.strftime('%Y-%m-%d')
    df = df.dropna(subset=['day'])

    if df.empty:
        return None

    if user_id is None:
        df = df.groupby('day').agg({'total_water_ml': 'sum'}).reset_index()

    if user_id:
        df['user'] = df['user__username']
    else:
        df['user'] = 'Всі користувачі'

    return df


def create_line_chart(df):
    if df is None:
        return None, "<p>Дані для графіка відсутні.</p>"

    fig = px.line(
        df,
        x='day',
        y='total_water_ml',
        title='Кількість спожитої води за останні 7 днів',
        labels={'day': 'Дата', 'total_water_ml': 'Вода (мл)'},
        markers=True
    )

    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)

    return chart_json


def calculate_statistics(df):
    if df is None or df.empty:
        return None

    stats = {
        'min': round(df['total_water_ml'].min(), 5),
        'max': round(df['total_water_ml'].max(), 5),
        'mean': round(df['total_water_ml'].mean(), 5),
        'median': round(df['total_water_ml'].median(), 5),
    }

    return stats


def water_intake_chart_view_pt(request):
    selected_user_id = request.GET.get('user', None)
    water_intake_data = get_water_intake_data(user_id=selected_user_id)
    data_frame = prepare_water_intake_dataframe(list(water_intake_data), user_id=selected_user_id)
    chart = create_line_chart(data_frame)
    statistics = calculate_statistics(data_frame)

    return render(request, 'dashboard/water_intake_per_weekday_pt.html', {
        'chart': chart,
        'users': User.objects.all(),
        'selected_user': selected_user_id,
        'data_table': list(water_intake_data),
        'statistics': statistics,
    })
