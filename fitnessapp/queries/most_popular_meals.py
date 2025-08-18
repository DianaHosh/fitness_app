from django.db.models import Count
from fitnessapp.models import Meal, User

def most_popular_meals_by_user():
    return Meal.objects.values(
        'user__username',
        'meal_type__food_name',
    ).annotate(
        total_orders=Count('meal_id')
    ).order_by('user__username', '-total_orders')
