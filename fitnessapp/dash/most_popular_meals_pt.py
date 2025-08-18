from django.shortcuts import render
import pandas as pd
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from django.db.models import Count
import json
from fitnessapp.models import Meal, User
from fitnessapp.queries.most_popular_meals import most_popular_meals_by_user
import numpy as np

def prepare_meal_dataframe(data):
    df = pd.DataFrame(data)

    if not df.empty:
        df = df.groupby('meal_type__food_name', as_index=False).agg({'total_orders': 'sum'})
        df = df.sort_values(by='total_orders', ascending=False).reset_index(drop=True)

    return df

def create_meal_pie_chart(df):
    if df.empty:
        return None, "<p>Дані для графіка відсутні.</p>"

    fig = px.pie(
        df,
        names='meal_type__food_name',
        values='total_orders',
        title="Популярність страв",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig.update_traces(textinfo='percent+label')

    graph_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graph_json

def calculate_statistics(df):
    if df.empty:
        return None, None, None, None

    min_val = df['total_orders'].min()
    max_val = df['total_orders'].max()
    avg_val = df['total_orders'].mean()
    median_val = df['total_orders'].median()

    return min_val, max_val, avg_val, median_val

def meal_popularity_analysis_pt(request):
    selected_user = request.GET.get('user', '')
    users = User.objects.all()

    meal_data = most_popular_meals_by_user()
    if selected_user:
        meal_data = meal_data.filter(user_id=selected_user)
    data = list(meal_data)

    df_meal = prepare_meal_dataframe(data)
    chart = create_meal_pie_chart(df_meal)

    min_val, max_val, avg_val, median_val = calculate_statistics(df_meal)

    return render(request, 'dashboard/meal_popularity_dash_pt.html', {
        'chart': chart,
        'users': users,
        'selected_user': str(selected_user),
        'data_table': data,
        'min_val': min_val,
        'max_val': max_val,
        'avg_val': avg_val,
        'median_val': median_val,
    })
