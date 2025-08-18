from concurrent.futures import ThreadPoolExecutor
import psycopg2
import time
import pandas as pd
import plotly.express as px
import psutil
from django.shortcuts import render

def pull_from_db():
    connection = psycopg2.connect(
        dbname='your_database',
        user='your_user',
        password='your_password',
        host='your_host',
        port='your_port'
    )
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT 
                v.first_name, v.last_name, m.title, s.show_date
            FROM Ticket t
            JOIN Showtime s ON t.showtime_id = s.id
            JOIN Viewer v ON t.viewer_id = v.id
            JOIN Movie m ON s.movie_id = m.id
            ORDER BY m.title;
        ''')
        records = cursor.fetchall()
    connection.close()
    return records

def multithreaded_execution(threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.submit(pull_from_db)
        result = future.result()
    return result

def threads_execution_time(request):
    time_stamps = {}

    for thread in range(2, 20, 2):
        start = time.time()
        result = multithreaded_execution(thread)
        end = time.time()
        execution_time = end - start
        time_stamps[thread] = execution_time

    df = pd.DataFrame(
        list(time_stamps.items()),
        columns=['thread', 'execution_time']
    )
    line_fig = px.line(df, x='thread', y='execution_time', title='Execution Time by Threads')
    graph_html = line_fig.to_html()

    start = time.time()
    result = multithreaded_execution(100)
    end = time.time()
    time_stamp = end - start

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    results = {
        'time': time_stamp,
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage
    }

    context = {
        'graph_html': graph_html,
        'results': results
    }

    return render(request, 'cinema/threads_execution.html', context)
