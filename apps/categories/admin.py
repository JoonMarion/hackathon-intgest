from django.contrib import admin

from apps.categories.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "kind", "user", "created_at")
    list_filter = ("kind", "created_at")
    search_fields = ("name",)
