from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView

from apps.categories.models import Category
from apps.transactions.http.filters import TransactionFilterSet
from apps.transactions.http.forms import TransactionForm
from apps.transactions.models import Transaction
from apps.transactions.services import (
    build_filtered_summary,
    resolve_selected_category_name,
)


class TransactionListView(LoginRequiredMixin, FilterView):
    model = Transaction
    filterset_class = TransactionFilterSet
    template_name = "transactions/pages/index.html"
    context_object_name = "transactions"

    ORDERING_DEFAULT = "-transaction_date,-created_at"
    ORDERING_OPTIONS = {
        "-transaction_date,-created_at": ("-transaction_date", "-created_at"),
        "transaction_date,created_at": ("transaction_date", "created_at"),
        "-amount,-created_at": ("-amount", "-created_at"),
        "amount,created_at": ("amount", "created_at"),
    }
    PAGE_SIZE_DEFAULT = 25
    PAGE_SIZE_OPTIONS = (10, 25, 50)

    def get_base_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related("category")

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs["queryset"] = self.get_base_queryset().order_by(*self.get_ordering_fields())
        kwargs["user"] = self.request.user
        return kwargs

    def get_ordering_value(self):
        ordering = self.request.GET.get("ordering", self.ORDERING_DEFAULT)
        if ordering in self.ORDERING_OPTIONS:
            return ordering
        return self.ORDERING_DEFAULT

    def get_ordering_fields(self):
        return self.ORDERING_OPTIONS[self.get_ordering_value()]

    def get_page_size(self):
        page_size = self.request.GET.get("page_size", "")
        if page_size.isdigit():
            page_size_value = int(page_size)
            if page_size_value in self.PAGE_SIZE_OPTIONS:
                return page_size_value
        return self.PAGE_SIZE_DEFAULT

    def get_paginate_by(self, queryset):
        del queryset
        return self.get_page_size()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(user=self.request.user).order_by("name")
        current_filters = {
            "q": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "kind": self.request.GET.get("kind", ""),
            "date_from": self.request.GET.get("date_from", ""),
            "date_to": self.request.GET.get("date_to", ""),
        }
        filterset = context.get("filter")
        summary_queryset = filterset.qs if filterset is not None else self.get_base_queryset()

        context["categories"] = categories
        context["current_filters"] = current_filters
        context["has_active_filters"] = any(current_filters.values())
        context["selected_category_name"] = resolve_selected_category_name(
            categories,
            current_filters["category"],
        )
        context["filtered_summary"] = build_filtered_summary(summary_queryset)
        context["current_ordering"] = self.get_ordering_value()
        context["current_page_size"] = self.get_page_size()
        context["ordering_options"] = tuple(self.ORDERING_OPTIONS.keys())
        context["page_size_options"] = self.PAGE_SIZE_OPTIONS
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/pages/form.html"
    success_url = reverse_lazy("transactions_http:index")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Transação criada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível criar a transação. Verifique os campos informados.")
        return super().form_invalid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = "transactions/pages/form.html"
    success_url = reverse_lazy("transactions_http:index")

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Transação atualizada com sucesso.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Não foi possível atualizar a transação. Verifique os campos informados.")
        return super().form_invalid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "transactions/pages/confirm_delete.html"
    success_url = reverse_lazy("transactions_http:index")

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        transaction = self.get_object()
        label = transaction.description.strip() if transaction.description else f"{transaction.get_kind_display()} {transaction.amount}"
        messages.success(self.request, f"Transação '{label}' removida com sucesso.")
        return super().form_valid(form)
