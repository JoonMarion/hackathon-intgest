from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.categories.models import Category
from apps.transactions.http.forms import TransactionForm
from apps.transactions.models import Transaction


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/pages/index.html"
    context_object_name = "transactions"

    def get_queryset(self):
        qs = (
            Transaction.objects.filter(user=self.request.user)
            .select_related("category")
            .order_by("-transaction_date", "-created_at")
        )

        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(description__icontains=q)

        category = self.request.GET.get("category", "").strip()
        if category:
            qs = qs.filter(category_id=category)

        kind = self.request.GET.get("kind", "").strip()
        if kind:
            qs = qs.filter(kind=kind)

        date_from = self.request.GET.get("date_from", "").strip()
        if date_from:
            qs = qs.filter(transaction_date__gte=date_from)

        date_to = self.request.GET.get("date_to", "").strip()
        if date_to:
            qs = qs.filter(transaction_date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = (
            Category.objects.filter(user=self.request.user).order_by("name")
        )
        context["current_filters"] = {
            "q": self.request.GET.get("q", ""),
            "category": self.request.GET.get("category", ""),
            "kind": self.request.GET.get("kind", ""),
            "date_from": self.request.GET.get("date_from", ""),
            "date_to": self.request.GET.get("date_to", ""),
        }
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
