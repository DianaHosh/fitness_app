from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from rest_framework import permissions, viewsets
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import date
from django.utils import timezone
from fitnessapp.serializers import (
    MealSerializer, WorkoutSerializer, SleepSerializer,
    WaterIntakeSerializer, MealTypeSerializer, WorkoutTypeSerializer,
    UserSerializer, DailySummarySerializer
)
from django.contrib.auth.models import User
from fitnessapp.models import (
    DailySummary, MealType, Meal,
    Sleep, WaterIntake, WorkoutType, Workout
)
from .models import DailySummary
from django.utils.timezone import now, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django import forms

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Електронна пошта")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ім’я'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Прізвище'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ім’я користувача'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }
@login_required
def edit_profile(request):
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('edit_profile')
    else:
        profile_form = ProfileEditForm(instance=request.user)
    return render(request, 'edit_profile.html', {
        'profile_form': profile_form,
    })
@login_required
def change_password(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            return redirect('edit_profile')
    else:
        password_form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {
        'password_form': password_form,
    })


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
@login_required
def calories_consumed(request):
    meals = Meal.objects.filter(user=request.user)
    return render(request, 'calories_consumed2.html', {'meals': meals})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def edit_meal(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    meal_types = MealType.objects.all()
    if request.method == 'POST':
        meal.meal_type = MealType.objects.get(meal_type_id=request.POST['meal_type'])
        meal.meal_date = request.POST['meal_date']
        meal.quantity_in_g = request.POST['quantity_in_g']
        meal.save()
        return redirect('calories_consumed')
    return render(request, 'edit_meal2.html', {'meal': meal, 'meal_types': meal_types})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def delete_meal(request, meal_id):
    meal = get_object_or_404(Meal, pk=meal_id)
    meal.delete()
    return redirect('calories_consumed')


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
@login_required
def calories_burned(request):
    workouts = Workout.objects.filter(user=request.user)
    return render(request, 'calories_burned2.html', {'workouts': workouts})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    workout_types = WorkoutType.objects.all()

    if request.method == 'POST':
        workout.workout_type = WorkoutType.objects.get(workout_type_id=request.POST['workout_type'])
        workout.workout_time_begin = request.POST['start_time']
        workout.workout_time_end = request.POST['end_time']
        workout.save()
        return redirect('calories_burned')

    return render(request, 'edit_workout2.html', {'workout': workout, 'workout_types': workout_types})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, pk=workout_id)
    workout.delete()
    return redirect('calories_burned')


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
@login_required
def sleep_stats(request):
    sleep_records = Sleep.objects.filter(user=request.user)
    return render(request, 'sleep_stats2.html', {'sleep_records': sleep_records})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def edit_sleep(request, sleep_id):
    sleep_record = get_object_or_404(Sleep, pk=sleep_id)
    if request.method == 'POST':
        sleep_record.sleep_time_begin = request.POST['sleep_time_begin']
        sleep_record.sleep_time_end = request.POST['sleep_time_end']
        sleep_record.save()
        return redirect('sleep_stats')

    return render(request, 'edit_sleep2.html', {'sleep_record': sleep_record})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def delete_sleep(request, sleep_id):
    sleep_record = get_object_or_404(Sleep, pk=sleep_id)
    sleep_record.delete()
    return redirect('sleep_stats')


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
@login_required
def water_intake(request):
    water_intakes = WaterIntake.objects.filter(user=request.user)
    for intake in water_intakes:
        intake.glasses *= 250
    return render(request, 'water_intake2.html', {'water_intakes': water_intakes})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def edit_water(request, water_intake_id):
    water_intake = get_object_or_404(WaterIntake, pk=water_intake_id)
    if request.method == 'POST':
        water_intake.glasses = request.POST['glasses']
        water_intake.intake_time = request.POST['intake_time']
        water_intake.save()
        return redirect('water_intake')

    return render(request, 'edit_water2.html', {'water_intake': water_intake})
@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def delete_water(request, water_intake_id):
    water_intake = get_object_or_404(WaterIntake, pk=water_intake_id)
    water_intake.delete()
    return redirect('water_intake')

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        response = JsonResponse({'message': 'Login successful'})
        response.set_cookie('jwt_token', str(refresh.access_token), httponly=True)
        return response
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=400)


def jwt_cookie_auth_middleware(get_response):
    def middleware(request):
        token = request.COOKIES.get('jwt_token')
        if token:
            jwt_auth = JWTAuthentication()
            try:
                user, _ = jwt_auth.get_user(validated_token=jwt_auth.get_validated_token(token))
                request.user = user
            except AuthenticationFailed:
                request.user = None
        return get_response(request)
    return middleware

@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def home(request):
    current_date = date.today()
    stats = DailySummary.objects.filter(user=request.user, summary_date=current_date).first()

    context = {
        "current_date": current_date,
        "stats": stats
    }
    return render(request, "home2.html", context)


@api_view(['GET', 'POST'])
@login_required
# @permission_classes([IsAuthenticated])
def add_meal(request):
    if request.method == 'POST':
        meal_type_id = request.POST.get('meal_type')
        quantity_in_g = request.POST.get('quantity_in_g')
        meal_date = request.POST.get('meal_date')

        if not meal_date:
            meal_date = timezone.now()

        meal_type = MealType.objects.get(meal_type_id=meal_type_id)

        Meal.objects.create(
            user=request.user,
            meal_type=meal_type,
            quantity_in_g=quantity_in_g,
            meal_date=meal_date,
        )
        return redirect('home')

    meal_types = MealType.objects.all()
    return render(request, 'add_meal2.html', {'meal_types': meal_types})


@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def add_sleep(request):
    if request.method == 'POST':
        sleep_time_begin = request.POST.get('sleep_time_begin')
        sleep_time_end = request.POST.get('sleep_time_end')
        calories_burned = request.POST.get('calories_burned', None)

        Sleep.objects.create(
            user=request.user,
            sleep_time_begin=sleep_time_begin,
            sleep_time_end=sleep_time_end,
            calories_burned=calories_burned or 0
        )
        return redirect('home')

    return render(request, 'add_sleep2.html')


@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def add_workout(request):
    workout_types = WorkoutType.objects.all()
    if request.method == 'POST':
        workout_type_id = request.POST.get('workout_type')
        workout_time_begin = request.POST.get('start_time')
        workout_time_end = request.POST.get('end_time')
        workout_type = WorkoutType.objects.get(workout_type_id=workout_type_id)

        Workout.objects.create(
            user=request.user,
            workout_type=workout_type,
            workout_time_begin=workout_time_begin,
            workout_time_end=workout_time_end,
        )
        return redirect('home')

    return render(request, 'add_workout2.html', {'workout_types': workout_types})


@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def add_water(request):
    if request.method == 'POST':
        glasses = request.POST.get('glasses')
        intake_time = request.POST.get('intake_date')

        if not intake_time:
            intake_time = timezone.now()

        WaterIntake.objects.create(
            user=request.user,
            glasses=glasses,
            intake_time=intake_time,
        )
        return redirect('home')

    return render(request, 'add_water2.html')

@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def add_workout_type(request):
    if request.method == 'POST':
        type_of_workout = request.POST.get('type_of_workout')
        calories_burned_per_hour = request.POST.get('calories_burned_per_hour')

        WorkoutType.objects.create(
            type_of_workout=type_of_workout,
            calories_burned_per_hour=calories_burned_per_hour
        )
        return redirect('home')
    return render(request, 'add_workout_type2.html')


@api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@login_required
def add_meal_type(request):
    if request.method == 'POST':
        food_name = request.POST.get('food_name')
        calories_per_100_g = request.POST.get('calories_per_100_g')

        MealType.objects.create(
            food_name=food_name,
            calories_per_100_g=calories_per_100_g
        )
        return redirect('home')
    return render(request, 'add_meal_type2.html')


class MealTypeViewSet(viewsets.ModelViewSet):
    queryset = MealType.objects.all().order_by('food_name')
    serializer_class = MealTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkoutTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkoutType.objects.all().order_by('type_of_workout')
    serializer_class = WorkoutTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all().order_by('meal_date')
    serializer_class = MealSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SleepViewSet(viewsets.ModelViewSet):
    queryset = Sleep.objects.all().order_by('sleep_time_begin')
    serializer_class = SleepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WaterIntakeViewSet(viewsets.ModelViewSet):
    queryset = WaterIntake.objects.all().order_by('intake_time')
    serializer_class = WaterIntakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WorkoutViewSet(viewsets.ModelViewSet):
    queryset = Workout.objects.all().order_by('workout_time_begin')
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DailySummaryViewSet(viewsets.ModelViewSet):
    queryset = DailySummary.objects.all().order_by('summary_date')
    serializer_class = DailySummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)