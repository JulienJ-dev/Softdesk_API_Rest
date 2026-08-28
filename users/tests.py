from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class UserApiTests(APITestCase):
    def setUp(self):
        self.password = 'Password123!'
        self.user = User.objects.create_user(
            username='alice',
            password=self.password,
            age=25,
        )
        User.objects.create_user(
            username='bob',
            password=self.password,
            age=30,
        )

    def authenticate(self):
        response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': self.user.username, 'password': self.password},
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_create_user(self):
        data = {
            'username': 'charlie',
            'password': 'AnotherPassword123!',
            'age': 18,
            'can_be_contacted': True,
            'can_data_be_shared': False,
        }

        response = self.client.post(reverse('user-list'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        self.assertTrue(
            User.objects.get(username='charlie').check_password(
                data['password']
            )
        )

    def test_reject_user_under_15(self):
        data = {
            'username': 'young_user',
            'password': 'AnotherPassword123!',
            'age': 14,
        }

        response = self.client.post(reverse('user-list'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_password_similar_to_username(self):
        data = {
            'username': 'longsimilarname123',
            'password': 'longsimilarname123',
            'age': 20,
        }

        response = self.client.post(reverse('user-list'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_authenticated_user_can_read_and_update_profile(self):
        self.authenticate()

        list_response = self.client.get(reverse('user-list'))
        detail_response = self.client.get(
            reverse('user-detail', args=[self.user.pk])
        )
        update_response = self.client.patch(
            reverse('user-detail', args=[self.user.pk]),
            {'can_be_contacted': True},
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['results']), 1)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertTrue(update_response.data['can_be_contacted'])

    def test_authenticated_user_can_delete_profile(self):
        self.authenticate()

        response = self.client.delete(
            reverse('user-detail', args=[self.user.pk])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
