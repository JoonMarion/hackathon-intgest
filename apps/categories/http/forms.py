from django import forms
from django.core.exceptions import ValidationError

from apps.categories.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "kind"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        self.fields["name"].error_messages["required"] = "Informe o nome da categoria."
        self.fields["kind"].error_messages["required"] = "Selecione o tipo da categoria."

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if not name:
            raise ValidationError("Informe um nome de categoria válido.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        kind = cleaned_data.get("kind")

        if not self.user or not name or not kind:
            return cleaned_data

        duplicate_qs = Category.objects.filter(user=self.user, kind=kind, name__iexact=name)
        if self.instance.pk:
            duplicate_qs = duplicate_qs.exclude(pk=self.instance.pk)

        if duplicate_qs.exists():
            self.add_error("name", "Você já possui uma categoria com esse nome para este tipo.")

        return cleaned_data
