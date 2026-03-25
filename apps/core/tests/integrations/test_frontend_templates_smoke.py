from django.urls import reverse

from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import UserFactory


class FrontendTemplatesSmokeTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="frontend-smoke", email="frontend-smoke@example.com")

    def test_auth_pages_render(self):
        login_response = self.client.get(reverse("accounts_http:login"))
        register_response = self.client.get(reverse("accounts_http:register"))

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(register_response.status_code, 200)

    def test_main_pages_render_for_authenticated_user(self):
        self.client.force_login(self.user)

        dashboard_response = self.client.get(reverse("core_http:index"))
        categories_response = self.client.get(reverse("categories_http:index"))
        transactions_response = self.client.get(reverse("transactions_http:index"))

        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(categories_response.status_code, 200)
        self.assertEqual(transactions_response.status_code, 200)
