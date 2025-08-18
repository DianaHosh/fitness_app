from django.shortcuts import render
from django.db.models import Count
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Category20
from fitnessapp.models import Meal, User
from fitnessapp.queries.most_popular_meals import most_popular_meals_by_user
import pandas as pd
from math import pi
import numpy as np
from bokeh.models import ColumnDataSource, LabelSet

def prepare_meal_dataframe(data):
    df = pd.DataFrame(data)

    if not df.empty:
        df = df.groupby('meal_type__food_name', as_index=False).agg({'total_orders': 'sum'})
        df = df.sort_values(by='total_orders', ascending=False).reset_index(drop=True)

    return df

def create_meal_pie_chart(df):
    required_columns = {'meal_type__food_name', 'total_orders'}
    if df.empty or not required_columns.issubset(df.columns):
        return None, "<p>Дані для графіка відсутні або неповні.</p>"

    try:
        food_names = df['meal_type__food_name'].tolist()
        total_orders = df['total_orders'].tolist()

        total = sum(total_orders)
        angles = [order / total * 2 * pi for order in total_orders]
        percentages = [f"{(order / total) * 100:.1f}%" for order in total_orders]
        colors = Category20[max(3, min(len(total_orders), 20))]

        start_angles = np.cumsum([0] + angles[:-1])
        end_angles = np.cumsum(angles)

        source = ColumnDataSource(data=dict(
            food_names=food_names,
            colors=colors,
            start_angles=start_angles,
            end_angles=end_angles,
            percentages=percentages,
            x=[0.4 * np.cos((start + end) / 2) for start, end in zip(start_angles, end_angles)],
            y=[0.4 * np.sin((start + end) / 2) for start, end in zip(start_angles, end_angles)]
        ))

        fig = figure(
            title="Популярність страв",
            toolbar_location=None,
            tools="",
            x_range=(-1, 1),
            y_range=(-1, 1),
        )

        fig.wedge(
            x=0,
            y=0,
            radius=0.5,
            start_angle='start_angles',
            end_angle='end_angles',
            color='colors',
            legend_field='food_names',
            source=source
        )

        labels = LabelSet(
            x='x',
            y='y',
            text='percentages',
            source=source,
            text_align='center',
            text_baseline='middle'
        )
        fig.add_layout(labels)

        fig.legend.title = "Страви"
        fig.axis.visible = False
        fig.grid.grid_line_color = None

        script, div = components(fig)
        return script, div

    except Exception as e:
        print(f"Помилка при створенні графіка: {e}")
        return None, "<p>Сталася помилка під час створення графіка.</p>"

def calculate_statistics(df):
    if df.empty:
        return None, None, None, None

    min_val = df['total_orders'].min()
    max_val = df['total_orders'].max()
    avg_val = df['total_orders'].mean()
    median_val = df['total_orders'].median()

    return min_val, max_val, avg_val, median_val

def meal_popularity_analysis_bk(request):
    selected_user = request.GET.get('user', '')
    selected_user = int(selected_user) if selected_user.isdigit() else None

    users = User.objects.all()
    meal_data = most_popular_meals_by_user()
    if selected_user:
        meal_data = meal_data.filter(user_id=selected_user)
    data = list(meal_data)
    df_meal = prepare_meal_dataframe(data)

    chart_script, chart_div = create_meal_pie_chart(df_meal)
    min_val, max_val, avg_val, median_val = calculate_statistics(df_meal)

    return render(request, 'dashboard/meal_popularity_dash_bk.html', {
        'chart_script': chart_script,
        'chart_div': chart_div,
        'users': users,
        'selected_user': selected_user,
        'data_table': data,
        'min_val': min_val,
        'max_val': max_val,
        'avg_val': avg_val,
        'median_val': median_val,
    })
