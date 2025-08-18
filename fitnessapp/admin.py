from django.contrib import admin
from fitnessapp.models import DailySummary, MealType, Meal, Sleep, WaterIntake, WorkoutType, Workout
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.register(DailySummary)
admin.site.register(MealType)
admin.site.register(Meal)
admin.site.register(Sleep)
admin.site.register(WaterIntake)
admin.site.register(WorkoutType)
admin.site.register(Workout)
