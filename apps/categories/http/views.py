from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.categories.http.forms import CategoryForm
from apps.categories.models import Category


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "categories/pages/index.html"
    context_object_name = "categories"

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = context.get("categories") or []
        context["income_categories"] = [category for category in categories if category.kind == Category.Kind.INCOME]
        context["expense_categories"] = [category for category in categories if category.kind == Category.Kind.EXPENSE]
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "categories/pages/form.html"
    success_url = reverse_lazy("categories_http:index")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Categoria criada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível criar a categoria. Verifique os campos informados.")
        return super().form_invalid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "categories/pages/form.html"
    success_url = reverse_lazy("categories_http:index")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Categoria atualizada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar a categoria. Verifique os campos informados.")
        return super().form_invalid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "categories/pages/confirm_delete.html"
    success_url = reverse_lazy("categories_http:index")

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        category = self.get_object()
        messages.success(self.request, f"Categoria '{category.name}' removida com sucesso.")
        return super().form_valid(form)
