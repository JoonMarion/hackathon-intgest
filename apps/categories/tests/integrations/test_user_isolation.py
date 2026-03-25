from django.urls import reverse

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, UserFactory


class CategoryUserIsolationTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user_a = UserFactory(username="categories-user-a", email="categories-user-a@example.com")
        self.user_b = UserFactory(username="categories-user-b", email="categories-user-b@example.com")
        self.category_a = CategoryFactory(
            user=self.user_a,
            name="Categoria A",
            kind=Category.Kind.EXPENSE,
        )
        self.category_b = CategoryFactory(
            user=self.user_b,
            name="Categoria B",
            kind=Category.Kind.INCOME,
        )

    def test_user_only_sees_own_categories(self):
        self.client.force_login(self.user_a)

        response = self.client.get(reverse("categories_http:index"))

        self.assertEqual(response.status_code, 200)
        categories = response.context["categories"]
        self.assertQuerySetEqual(categories, [self.category_a], transform=lambda item: item)
        self.assertNotIn(self.category_b, categories)