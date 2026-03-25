from django.test import TestCase
from django.urls import reverse


class AuthProtectionTests(TestCase):
    def test_anonymous_user_is_redirected_to_login_for_protected_pages(self):
        login_url = reverse("accounts_http:login")
        protected_urls = [
            reverse("core_http:index"),
            reverse("categories_http:index"),
            reverse("transactions_http:index"),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{login_url}?next={url}",
                    fetch_redirect_response=False,
                )