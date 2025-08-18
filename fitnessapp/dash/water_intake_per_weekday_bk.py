from django.db.models import Sum, F, Value
from django.db.models.functions import Cast
from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import render
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components
from fitnessapp.models import WaterIntake, User
from django.db.models import DateField
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


def create_bokeh_chart(df):
    if df is None:
        return None, "<p>Дані для графіка відсутні.</p>"

    p = figure(x_axis_label='Дата', y_axis_label='Вода (мл)', title='Кількість спожитої води за останні 7 днів',
               x_axis_type='datetime', height=400, width=800)

    dates = pd.to_datetime(df['day'])
    total_water = df['total_water_ml']

    p.line(dates, total_water, legend_label="Вода (мл)", line_width=2, color="blue")
    p.circle(dates, total_water, size=6, color="red", alpha=0.5)

    script, div = components(p)

    return script, div


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


def water_intake_chart_view_bk(request):
    selected_user_id = request.GET.get('user', None)
    water_intake_data = get_water_intake_data(user_id=selected_user_id)
    data_frame = prepare_water_intake_dataframe(list(water_intake_data), user_id=selected_user_id)
    script, div = create_bokeh_chart(data_frame)
    statistics = calculate_statistics(data_frame)

    return render(request, 'dashboard/water_intake_per_weekday_bk.html', {
        'script': script,
        'div': div,
        'users': User.objects.all(),
        'selected_user': selected_user_id,
        'data_table': list(water_intake_data),
        'statistics': statistics
    })
