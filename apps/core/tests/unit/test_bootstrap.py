from django.test import SimpleTestCase
from django.urls import resolve


class CoreBootstrapTests(SimpleTestCase):
    def test_http_route_resolves(self):
        match = resolve("/core/")
        self.assertEqual(match.url_name, "index")
