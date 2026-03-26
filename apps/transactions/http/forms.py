from django import forms
from django.core.exceptions import ValidationError

from apps.categories.models import Category
from apps.transactions.models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["category", "kind", "amount", "transaction_date", "description", "notes"]
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3, "maxlength": "500"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["category"].widget.attrs.update({"data-e2e-selector": "transactions-form-category-select"})
        self.fields["kind"].widget.attrs.update({"data-e2e-selector": "transactions-form-kind-select"})
        self.fields["amount"].widget.attrs.update({"data-e2e-selector": "transactions-form-amount-input"})
        self.fields["transaction_date"].widget.attrs.update({"data-e2e-selector": "transactions-form-transaction-date-input"})
        self.fields["description"].widget.attrs.update({"data-e2e-selector": "transactions-form-description-input"})
        self.fields["notes"].widget.attrs.update({"data-e2e-selector": "transactions-form-notes-input"})

        self.fields["category"].error_messages["required"] = "Selecione uma categoria."
        self.fields["kind"].error_messages["required"] = "Selecione o tipo da transação."
        self.fields["amount"].error_messages["required"] = "Informe o valor da transação."
        self.fields["transaction_date"].error_messages["required"] = "Informe a data da transação."

        category_queryset = Category.objects.none()
        if self.user:
            category_queryset = Category.objects.filter(user=self.user).order_by("name")
        self.fields["category"].queryset = category_queryset

    def get_initial_for_field(self, field, field_name):
        val = super().get_initial_for_field(field, field_name)
        if field_name == "transaction_date" and val:
            return val.isoformat()
        return val

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= 0:
            raise ValidationError("Informe um valor maior que zero.")
        return amount

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if category is None:
            return category

        if self.user and category.user_id != self.user.id:
            raise ValidationError("Selecione uma categoria válida da sua conta.")

        return category

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        kind = cleaned_data.get("kind")

        if category and kind and category.kind != kind:
            self.add_error("kind", "O tipo da transação deve ser compatível com o tipo da categoria.")

        return cleaned_data
