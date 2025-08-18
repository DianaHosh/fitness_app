from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from fitnessapp.models import Meal, MealType, Workout, WorkoutType
from django.utils.timezone import now, timedelta


class WorkoutApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpassword')
        self.workout_type = WorkoutType.objects.create(type_of_workout="Rowing", calories_burned_per_hour=600)
        self.client.login(username='tester', password='testpassword')

    def test_create_and_get_workout(self):
        workout_data = {
            "user": self.user.id,
            "workout_type": self.workout_type.workout_type_id,
            "workout_time_begin": now().isoformat(),
            "workout_time_end": (now() + timedelta(hours=1)).isoformat()
        }

        response = self.client.post('/api/workouts/', workout_data, format='json')

        self.assertEqual(response.status_code, 201)
        workout_id = response.json()['workout_id']
        get_response = self.client.get(f'/api/workouts/{workout_id}/')
        self.assertEqual(get_response.status_code, 200)
        workout = get_response.json()

        self.assertEqual(workout['user'], f'http://testserver/api/users/{self.user.id}/')
        self.assertEqual(workout['workout_type'], self.workout_type.workout_type_id)


if __name__ == '__main__':
    unittest.main()
