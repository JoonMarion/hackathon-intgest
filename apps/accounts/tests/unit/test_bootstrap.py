from django.test import SimpleTestCase
from django.urls import resolve


class AccountsBootstrapTests(SimpleTestCase):
    def test_http_route_resolves(self):
        match = resolve("/accounts/")
        self.assertEqual(match.url_name, "index")
