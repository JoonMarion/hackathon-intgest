from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import UserFactory

User = get_user_model()


class RegistrationFlowTests(BaseIntegrationTestCase):
    def test_register_page_loads(self):
        url = reverse("accounts_http:register")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        url = reverse("accounts_http:register")
        data = {
            "username": "auth-flow-user",
            "email": "auth-flow-user@example.com",
            "password1": "strong-pass-987!",
            "password2": "strong-pass-987!",
        }
        response = self.client.post(url, data)
        self.assertRedirects(
            response,
            reverse("accounts_http:login"),
            fetch_redirect_response=False,
        )
        user = User.objects.get(username="auth-flow-user")
        self.assertEqual(user.email, "auth-flow-user@example.com")

    def test_register_with_missing_email_shows_form_errors(self):
        url = reverse("accounts_http:register")
        data = {
            "username": "no-email-flow",
            "email": "",
            "password1": "strong-pass-987!",
            "password2": "strong-pass-987!",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "email", ["This field is required."])

    def test_register_with_duplicate_username_shows_error(self):
        UserFactory(username="dup-user")
        url = reverse("accounts_http:register")
        data = {
            "username": "dup-user",
            "email": "dup-user-new@example.com",
            "password1": "strong-pass-987!",
            "password2": "strong-pass-987!",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class LoginFlowTests(BaseIntegrationTestCase):
    def test_login_page_loads(self):
        url = reverse("accounts_http:login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_with_username_redirects_to_index(self):
        UserFactory(username="login-flow-user")
        url = reverse("accounts_http:login")
        response = self.client.post(
            url, {"username": "login-flow-user", "password": "test-pass-123"}
        )
        self.assertRedirects(
            response,
            reverse("core_http:index"),
            fetch_redirect_response=False,
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_email_redirects_to_index(self):
        UserFactory(username="email-flow-user", email="email-flow-user@example.com")
        url = reverse("accounts_http:login")
        response = self.client.post(
            url,
            {"username": "email-flow-user@example.com", "password": "test-pass-123"},
        )
        self.assertRedirects(
            response,
            reverse("core_http:index"),
            fetch_redirect_response=False,
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_credentials_shows_error(self):
        UserFactory(username="bad-cred-user")
        url = reverse("accounts_http:login")
        response = self.client.post(
            url, {"username": "bad-cred-user", "password": "wrong-password"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirects_to_login(self):
        user = UserFactory(username="logout-flow-user")
        self.client.force_login(user)
        url = reverse("accounts_http:logout")
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("accounts_http:login"),
            fetch_redirect_response=False,
        )
