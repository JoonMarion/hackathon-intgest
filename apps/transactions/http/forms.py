from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError

from apps.categories.models import Category
from apps.transactions.models import FinancialAccount, Transaction
from apps.transactions.services.import_export import ALLOWED_MAPPING_KEYS
from apps.transactions.services.import_export import REQUIRED_MAPPING_KEYS
from apps.transactions.services.import_export import ensure_user_minimum_account


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            "account",
            "category",
            "kind",
            "amount",
            "transaction_date",
            "payee",
            "description",
            "notes",
        ]
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3, "maxlength": "500"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["account"].widget.attrs.update({"data-e2e-selector": "transactions-form-account-select"})
        self.fields["category"].widget.attrs.update({"data-e2e-selector": "transactions-form-category-select"})
        self.fields["kind"].widget.attrs.update({"data-e2e-selector": "transactions-form-kind-select"})
        self.fields["amount"].widget.attrs.update({"data-e2e-selector": "transactions-form-amount-input"})
        self.fields["transaction_date"].widget.attrs.update({"data-e2e-selector": "transactions-form-transaction-date-input"})
        self.fields["payee"].widget.attrs.update({"data-e2e-selector": "transactions-form-payee-input"})
        self.fields["description"].widget.attrs.update({"data-e2e-selector": "transactions-form-description-input"})
        self.fields["notes"].widget.attrs.update({"data-e2e-selector": "transactions-form-notes-input"})

        self.fields["account"].error_messages["required"] = "Selecione uma conta."
        self.fields["category"].error_messages["required"] = "Selecione uma categoria."
        self.fields["kind"].error_messages["required"] = "Selecione o tipo da transação."
        self.fields["amount"].error_messages["required"] = "Informe o valor da transação."
        self.fields["transaction_date"].error_messages["required"] = "Informe a data da transação."

        category_queryset = Category.objects.none()
        account_queryset = FinancialAccount.objects.none()
        if self.user:
            ensure_user_minimum_account(user=self.user)
            category_queryset = Category.objects.filter(user=self.user).order_by("name")
            account_queryset = FinancialAccount.objects.filter(user=self.user, is_active=True).order_by("name")

        self.fields["category"].queryset = category_queryset
        self.fields["account"].queryset = account_queryset

        if self.user and not self.instance.pk:
            self.fields["account"].initial = account_queryset.first()

    def get_initial_for_field(self, field, field_name):
        value = super().get_initial_for_field(field, field_name)
        if field_name == "transaction_date" and value:
            return value.isoformat()
        return value

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None or amount <= 0:
            raise ValidationError("Informe um valor maior que zero.")
        return amount

    def clean_account(self):
        account = self.cleaned_data.get("account")
        if account is None:
            return account
        if self.user and account.user_id != self.user.id:
            raise ValidationError("Selecione uma conta válida da sua conta.")
        return account

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


class TransactionImportUploadForm(forms.Form):
    source_file = forms.FileField(label="Arquivo de importação")

    def clean_source_file(self):
        source_file = self.cleaned_data["source_file"]
        extension = Path(source_file.name).suffix.lower()
        if extension not in {".csv", ".xlsx"}:
            raise ValidationError("Envie um arquivo CSV ou XLSX.")
        if source_file.size <= 0:
            raise ValidationError("O arquivo está vazio.")
        return source_file


class TransactionImportMappingForm(forms.Form):
    date = forms.ChoiceField(label="Coluna Data")
    amount = forms.ChoiceField(label="Coluna Valor")
    payee = forms.ChoiceField(label="Coluna Favorecido")
    account = forms.ChoiceField(label="Coluna Conta")
    import_id = forms.ChoiceField(label="Coluna ImportId", required=False)
    description = forms.ChoiceField(label="Coluna Descrição", required=False)
    notes = forms.ChoiceField(label="Coluna Observação", required=False)
    category = forms.ChoiceField(label="Coluna Categoria", required=False)

    def __init__(self, *args, headers: list[str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        headers = headers or []
        options = [(header, header) for header in headers]
        optional_options = [("", "Não mapear")] + options

        for key in REQUIRED_MAPPING_KEYS:
            self.fields[key].choices = options

        for key in set(ALLOWED_MAPPING_KEYS) - set(REQUIRED_MAPPING_KEYS):
            self.fields[key].choices = optional_options

    def clean(self):
        cleaned_data = super().clean()

        required_values = [cleaned_data.get(key, "") for key in REQUIRED_MAPPING_KEYS]
        if len(required_values) != len(set(required_values)):
            raise ValidationError("Cada coluna obrigatória deve mapear um cabeçalho diferente.")

        selected_values = [
            cleaned_data.get(key, "")
            for key in ALLOWED_MAPPING_KEYS
            if cleaned_data.get(key, "")
        ]
        if len(selected_values) != len(set(selected_values)):
            raise ValidationError("Não repita o mesmo cabeçalho em múltiplos campos de mapeamento.")

        return cleaned_data
