from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()

class UserAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_logout(self):
        # Ensure the user is logged in
        self.assertTrue(self.client.login(username='testuser', password='testpassword'))

        # Check the user's initial authentication state
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)

        # Log the user out
        response = self.client.get(reverse('users:logout'))

        # Check the user's authentication state after logout
        user.refresh_from_db()
        self.assertFalse(user.is_authenticated)

        # Ensure the user is redirected to the login page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/users/login/')
