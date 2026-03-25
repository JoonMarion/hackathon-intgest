from django.test import SimpleTestCase
from django.urls import resolve


class CategoriesBootstrapTests(SimpleTestCase):
    def test_http_route_resolves(self):
        match = resolve("/categories/")
        self.assertEqual(match.url_name, "index")
