from concurrent.futures import ThreadPoolExecutor
import time
import pandas as pd
import plotly.express as px
import psutil
from django.shortcuts import render
from fitnessapp.models import Meal


def pull_meals_from_db(user_id):
    meals = Meal.objects.filter(user_id=user_id).select_related("meal_type").values(
        "meal_type__food_name", "calories", "meal_date"
    )
    return list(meals)


def multithreaded_execution(pull_meals_from_db, user_id, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.submit(pull_meals_from_db, user_id)
        result = future.result()
    return result


def threads_execution_time(request):
    user_id = request.GET.get('user_id', 1)
    time_stamps = {}
    threads = [1, 2, 4, 8, 16, 32]

    for thread in threads:
        start = time.time()
        result = multithreaded_execution(pull_meals_from_db, user_id, thread)
        end = time.time()
        execution_time = end - start
        time_stamps[thread] = execution_time

    fastest_thread = min(time_stamps, key=time_stamps.get)
    slowest_thread = max(time_stamps, key=time_stamps.get)

    df = pd.DataFrame(
        list(time_stamps.items()),
        columns=['Threads', 'Execution Time']
    )
    line_fig = px.line(df, x='Threads', y='Execution Time', title='Execution Time by Threads',
                       labels={"Threads": "Number of Threads", "Execution Time": "Time (s)"}, markers=True)
    graph_html = line_fig.to_html()

    start = time.time()
    result = multithreaded_execution(pull_meals_from_db, user_id, 200)
    end = time.time()
    time_stamp = end - start

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    results = {
        'time': time_stamp,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'fastest_thread': fastest_thread,
        'fastest_time': time_stamps[fastest_thread],
        'slowest_thread': slowest_thread,
        'slowest_time': time_stamps[slowest_thread]
    }

    context = {
        'graph_html': graph_html,
        'results': results
    }

    return render(request, 'experiment/dashboard.html', context)
