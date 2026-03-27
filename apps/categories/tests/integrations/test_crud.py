from datetime import timedelta

from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory


class CategoryCRUDIntegrationTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="categories-crud-user", email="categories-crud-user@example.com")
        self.other_user = UserFactory(
            username="categories-crud-other-user",
            email="categories-crud-other-user@example.com",
        )

    def test_list_requires_authentication(self):
        url = reverse("categories_http:index")
        login_url = reverse("accounts_http:login")

        response = self.client.get(url)

        self.assertRedirects(response, f"{login_url}?next={url}", fetch_redirect_response=False)

    def test_list_is_ordered_by_most_recent(self):
        self.client.force_login(self.user)
        older_category = CategoryFactory(user=self.user, name="Mais antiga", kind=Category.Kind.EXPENSE)
        newer_category = CategoryFactory(user=self.user, name="Mais recente", kind=Category.Kind.INCOME)

        now = timezone.now()
        Category.objects.filter(pk=older_category.pk).update(created_at=now - timedelta(days=1))
        Category.objects.filter(pk=newer_category.pk).update(created_at=now)

        response = self.client.get(reverse("categories_http:index"))

        self.assertEqual(response.status_code, 200)
        categories = list(response.context["categories"])
        self.assertEqual(categories, [newer_category, older_category])

    def test_list_exposes_summary_context(self):
        self.client.force_login(self.user)
        CategoryFactory(user=self.user, name="Salário", kind=Category.Kind.INCOME)
        CategoryFactory(user=self.user, name="Mercado", kind=Category.Kind.EXPENSE)

        response = self.client.get(reverse("categories_http:index"))

        summary = response.context["category_summary"]
        self.assertEqual(summary["total_count"], 2)
        self.assertEqual(summary["income_count"], 1)
        self.assertEqual(summary["expense_count"], 1)
        self.assertTrue(summary["has_both_kinds"])
        self.assertEqual(summary["newest_category"].name, "Mercado")

    def test_list_renders_future_import_export_actions(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("categories_http:index"))

        self.assertContains(response, "Importar categorias em breve")
        self.assertContains(response, "Exportar planilha em breve")

    def test_create_creates_category_for_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("categories_http:create"),
            data={
                "name": "Nova Categoria",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertRedirects(response, reverse("categories_http:index"))
        created = Category.objects.get(name="Nova Categoria")
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.kind, Category.Kind.EXPENSE)

    def test_update_changes_only_category_from_logged_in_user(self):
        own_category = CategoryFactory(user=self.user, name="Original", kind=Category.Kind.EXPENSE)
        other_category = CategoryFactory(user=self.other_user, name="Outra", kind=Category.Kind.INCOME)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("categories_http:update", args=[own_category.pk]),
            data={
                "name": "Atualizada",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertRedirects(response, reverse("categories_http:index"))
        own_category.refresh_from_db()
        other_category.refresh_from_db()
        self.assertEqual(own_category.name, "Atualizada")
        self.assertEqual(other_category.name, "Outra")

    def test_delete_removes_only_category_from_logged_in_user(self):
        own_category = CategoryFactory(user=self.user, name="Minha categoria", kind=Category.Kind.EXPENSE)
        other_category = CategoryFactory(user=self.other_user, name="Categoria de terceiro", kind=Category.Kind.INCOME)
        self.client.force_login(self.user)

        response = self.client.post(reverse("categories_http:delete", args=[own_category.pk]))

        self.assertRedirects(response, reverse("categories_http:index"))
        self.assertFalse(Category.objects.filter(pk=own_category.pk).exists())
        self.assertTrue(Category.objects.filter(pk=other_category.pk).exists())

    def test_update_from_another_user_category_returns_404(self):
        other_category = CategoryFactory(user=self.other_user, name="Protegida", kind=Category.Kind.EXPENSE)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("categories_http:update", args=[other_category.pk]),
            data={
                "name": "Não pode",
                "kind": Category.Kind.EXPENSE,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_from_another_user_category_returns_404(self):
        other_category = CategoryFactory(user=self.other_user, name="Protegida", kind=Category.Kind.EXPENSE)
        self.client.force_login(self.user)

        response = self.client.post(reverse("categories_http:delete", args=[other_category.pk]))

        self.assertEqual(response.status_code, 404)

    def test_delete_category_with_linked_transactions_shows_error(self):
        category = CategoryFactory(user=self.user, name="Com lançamentos", kind=Category.Kind.EXPENSE)
        TransactionFactory(user=self.user, category=category)
        self.client.force_login(self.user)

        response = self.client.post(reverse("categories_http:delete", args=[category.pk]))

        self.assertRedirects(response, reverse("categories_http:index"), fetch_redirect_response=False)
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())
        response_messages = list(messages.get_messages(response.wsgi_request))
        self.assertTrue(
            any("Não é possível excluir a categoria" in str(m) for m in response_messages),
        )
