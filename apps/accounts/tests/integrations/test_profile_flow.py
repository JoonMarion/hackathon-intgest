from django.urls import reverse

from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import UserFactory


class ProfileFlowTests(BaseIntegrationTestCase):
    def test_profile_requires_authentication(self):
        url = reverse("accounts_http:profile")
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"{reverse('accounts_http:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_profile_edit_requires_authentication(self):
        url = reverse("accounts_http:profile_edit")
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"{reverse('accounts_http:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_password_change_requires_authentication(self):
        url = reverse("accounts_http:password_change")
        response = self.client.get(url)
        self.assertRedirects(
            response,
            f"{reverse('accounts_http:login')}?next={url}",
            fetch_redirect_response=False,
        )

    def test_profile_page_loads_for_authenticated_user(self):
        user = UserFactory(
            username="profile-user",
            email="profile-user@example.com",
            first_name="Perfil",
            last_name="Usuario",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts_http:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Minha conta")
        self.assertContains(response, "profile-user@example.com")
        self.assertContains(response, reverse("accounts_http:profile_edit"))
        self.assertContains(response, reverse("accounts_http:password_change"))

    def test_profile_edit_updates_general_data(self):
        user = UserFactory(
            username="profile-edit-user",
            email="old-email@example.com",
            first_name="Nome",
            last_name="Antigo",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts_http:profile_edit"),
            {
                "username": "profile-edit-user",
                "email": "new-email@example.com",
                "first_name": "Novo",
                "last_name": "Sobrenome",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts_http:profile"),
            fetch_redirect_response=False,
        )
        user.refresh_from_db()
        self.assertEqual(user.email, "new-email@example.com")
        self.assertEqual(user.first_name, "Novo")
        self.assertEqual(user.last_name, "Sobrenome")

    def test_password_change_updates_user_password(self):
        user = UserFactory(username="password-flow-user")
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts_http:password_change"),
            {
                "old_password": "test-pass-123",
                "new_password1": "new-strong-pass-987!",
                "new_password2": "new-strong-pass-987!",
            },
        )

        self.assertRedirects(
            response,
            reverse("accounts_http:profile"),
            fetch_redirect_response=False,
        )

        user.refresh_from_db()
        self.assertTrue(user.check_password("new-strong-pass-987!"))

        self.client.logout()
        login_result = self.client.login(
            username="password-flow-user",
            password="new-strong-pass-987!",
        )
        self.assertTrue(login_result)
