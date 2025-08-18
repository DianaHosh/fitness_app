from fitnessapp.models import Sleep
from django.db.models import Sum, F

def get_top_sleep_data(start_date, end_date):
    query = Sleep.objects.filter(
        sleep_time_begin__gte=start_date,
        sleep_time_end__lte=end_date
    ).annotate(
        sleep_duration=F('duration')
    ).values('user__username').annotate(
        total_sleep=Sum('sleep_duration')
    ).order_by('-total_sleep')

    return list(query)
