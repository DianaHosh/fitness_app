from django.shortcuts import render
from fitnessapp.models import Sleep, User
from django.utils.timezone import make_aware, now
from datetime import datetime, timedelta
from django.db.models import Sum, F
from bokeh.plotting import figure
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource
import json
from bokeh.palettes import Category20
from fitnessapp.queries.top_sleep_users import get_top_sleep_data

def prepare_sleep_dataframe(data):
    import pandas as pd

    df = pd.DataFrame(data)
    if df.empty:
        return None

    df['total_sleep'] = pd.to_numeric(df['total_sleep'], errors='coerce')
    df['user'] = df['user__username']

    stats = {
        'min': round(df['total_sleep'].min(), 5),
        'max': round(df['total_sleep'].max(), 5),
        'mean': round(df['total_sleep'].mean(), 5),
        'median': round(df['total_sleep'].median(), 5)
    }

    return df, stats

def create_bar_chart(df):
    if df is None or df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    try:
        users = df['user'].unique()
        colors = Category20[max(len(users), 3)]
        source = ColumnDataSource(df)

        p = figure(x_range=users, title="Топ користувачі за часом сну",
                   x_axis_label='Користувачі',
                   y_axis_label='Загальна тривалість сну (години)',
                   height=400, width=700)

        for i, user in enumerate(users):
            user_data = df[df['user'] == user]
            p.vbar(x='user', top='total_sleep', source=source, width=0.5, color=colors[i % len(colors)])

        return json_item(p), None

    except KeyError as e:
        return None, f"<p>Помилка: {str(e)}. Перевірте, чи дані правильно підготовлені.</p>"


def sleep_chart_view_bk(request):
    start_date = request.GET.get('start_date', (now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', now().strftime('%Y-%m-%d'))
    start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
    end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

    sleep_data = get_top_sleep_data(start_date, end_date)
    data_frame, stats = prepare_sleep_dataframe(sleep_data)

    bar_chart, error_message = create_bar_chart(data_frame)
    bar_chart = json.dumps(bar_chart) if bar_chart else None

    context = {
        'chart': bar_chart,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'users': User.objects.all(),
        'data_table': sleep_data,
        'error_message': error_message,
        'stats': stats,
    }

    return render(request, 'dashboard/top_sleep_users_bk.html', context)
