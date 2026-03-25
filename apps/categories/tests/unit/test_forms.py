from apps.categories.http.forms import CategoryForm
from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, UserFactory


class CategoryFormTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="category-form-user", email="category-form-user@example.com")

    def test_name_is_required(self):
        form = CategoryForm(
            user=self.user,
            data={
                "name": "",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_name_with_only_whitespace_is_invalid(self):
        form = CategoryForm(
            user=self.user,
            data={
                "name": "   ",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["Informe o nome da categoria."])

    def test_duplicate_name_for_same_user_and_kind_is_invalid(self):
        CategoryFactory(
            user=self.user,
            name="Mercado",
            kind=Category.Kind.EXPENSE,
        )

        form = CategoryForm(
            user=self.user,
            data={
                "name": " mercado ",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["Você já possui uma categoria com esse nome para este tipo."])

    def test_same_name_with_different_kind_is_allowed(self):
        CategoryFactory(
            user=self.user,
            name="Salário",
            kind=Category.Kind.INCOME,
        )

        form = CategoryForm(
            user=self.user,
            data={
                "name": "Salário",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertTrue(form.is_valid())
