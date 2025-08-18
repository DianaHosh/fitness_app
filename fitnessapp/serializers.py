from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    DailySummary, MealType, Meal,
    Sleep, WaterIntake, WorkoutType, Workout,
)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'first_name', 'last_name']


class DailySummarySerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)

    class Meta:
        model = DailySummary
        fields = [
            'url',
            'user',
            'summary_date',
            'total_calories_consumed',
            'total_calories_burned',
            'total_water_intake_ml',
            'total_sleep_time',
        ]


class MealTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MealType
        fields = ['url', 'meal_type_id', 'food_name', 'calories_per_100_g']


class MealSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)
    # meal_type = serializers.HyperlinkedRelatedField(view_name='mealtype-detail', read_only=True)
    meal_type = serializers.PrimaryKeyRelatedField(queryset=MealType.objects.all())

    class Meta:
        model = Meal
        fields = [
            'url',
            'meal_id',
            'user',
            'meal_type',
            'meal_date',
            'quantity_in_g',
            'calories',
        ]


class SleepSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)

    class Meta:
        model = Sleep
        fields = [
            'url',
            'sleep_id',
            'user',
            'sleep_time_begin',
            'sleep_time_end',
            'duration',
            'calories_burned',
        ]


class WaterIntakeSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(view_name='user-detail', read_only=True)

    class Meta:
        model = WaterIntake
        fields = ['url', 'intake_id', 'user', 'intake_time', 'glasses']


class WorkoutTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkoutType
        fields = ['url', 'workout_type_id', 'type_of_workout', 'calories_burned_per_hour']


class WorkoutSerializer(serializers.HyperlinkedModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    workout_type = serializers.PrimaryKeyRelatedField(queryset=WorkoutType.objects.all())

    class Meta:
        model = Workout
        fields = [
            'url',
            'workout_id',
            'user',
            'workout_type',
            'workout_time_begin',
            'workout_time_end',
            'duration',
            'burned_calories',
        ]
        read_only_fields = ['user']
