from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.transactions.models import Transaction


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/pages/index.html"
    context_object_name = "transactions"

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related("category")
