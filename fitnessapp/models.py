from django.db import models
from django.contrib.auth.models import User


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class MealType(models.Model):
    meal_type_id = models.AutoField(primary_key=True)
    food_name = models.CharField(max_length=100, blank=True, null=True)
    calories_per_100_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'meal_type'

    def __str__(self):
        return self.food_name


class Meal(models.Model):
    meal_id = models.AutoField(primary_key=True)
    meal_type = models.ForeignKey('MealType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    meal_date = models.DateTimeField(blank=True, null=True)
    quantity_in_g = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    calories = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'meal'
        unique_together = ('user', 'meal_type', 'meal_date')

    def __str__(self):
        return f'{self.user.username} - {self.meal_type.food_name} - {self.meal_date}'


class Sleep(models.Model):
    sleep_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    sleep_time_begin = models.DateTimeField(blank=True, null=True)
    sleep_time_end = models.DateTimeField(blank=True, null=True)
    duration = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    calories_burned = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'sleep'
        unique_together = ('user', 'sleep_time_begin', 'sleep_time_end')

    def __str__(self):
        return f'{self.user.username} - {self.sleep_time_begin} - {self.sleep_time_end}'


class WaterIntake(models.Model):
    intake_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    intake_time = models.DateTimeField(blank=True, null=True)
    glasses = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'water_intake'
        unique_together = ('user', 'intake_time')

    def __str__(self):
        return f'{self.user.username} - {self.intake_time}'


class WorkoutType(models.Model):
    workout_type_id = models.AutoField(primary_key=True)
    type_of_workout = models.CharField(max_length=50, blank=True, null=True)
    calories_burned_per_hour = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'workout_type'

    def __str__(self):
        return self.type_of_workout


class Workout(models.Model):
    workout_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    workout_type = models.ForeignKey('WorkoutType', models.DO_NOTHING, blank=True, null=True)
    workout_time_begin = models.DateTimeField(blank=True, null=True)
    workout_time_end = models.DateTimeField(blank=True, null=True)
    duration = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    burned_calories = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'workout'
        unique_together = ('user', 'workout_type', 'workout_time_begin', 'workout_time_end')

    def __str__(self):
        return f'{self.user.username} - {self.workout_type.type_of_workout} - {self.workout_time_begin} - {self.workout_time_end}'


class DailySummary(models.Model):
    summary_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    summary_date = models.DateField(blank=True, null=True)
    total_calories_consumed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    total_calories_burned = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    total_water_intake_ml = models.IntegerField(blank=True, null=True)
    total_sleep_time = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'daily_summary'
        unique_together = ('user', 'summary_date')

    def __str__(self):
        return f'{self.user.username} - {self.summary_date}'
