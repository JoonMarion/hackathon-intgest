from django.test import SimpleTestCase
from django.urls import resolve


class TransactionsBootstrapTests(SimpleTestCase):
    def test_http_route_resolves(self):
        match = resolve("/transactions/")
        self.assertEqual(match.url_name, "index")
