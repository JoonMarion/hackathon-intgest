from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.categories.models import Category


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "categories/pages/index.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
