from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.models import BaseModel, CategoryKind


class Category(BaseModel):
    Kind = CategoryKind

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(_("Nome"), max_length=120)

    kind = models.CharField(
        _("Tipo"),
        max_length=20,
        choices=CategoryKind.choices,
    )

    class Meta:
        """Model options intentionally explicit without schema-impacting settings."""

    def __str__(self) -> str:
        return self.name
