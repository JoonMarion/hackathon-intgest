import django_filters

from apps.categories.models import Category
from apps.transactions.models import Transaction


class TransactionFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.none())
    kind = django_filters.ChoiceFilter(choices=Transaction.Kind.choices)
    date_from = django_filters.DateFilter(field_name="transaction_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="transaction_date", lookup_expr="lte")

    class Meta:
        model = Transaction
        fields = ["q", "category", "kind", "date_from", "date_to"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.filters["category"].queryset = Category.objects.filter(user=user).order_by("name")

    def filter_q(self, queryset, name, value):
        del name
        if not value:
            return queryset
        from django.db.models import Q

        return queryset.filter(Q(description__icontains=value) | Q(notes__icontains=value))