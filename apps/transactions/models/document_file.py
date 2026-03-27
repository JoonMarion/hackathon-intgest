from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.models import BaseModel


class DocumentFile(BaseModel):
    class Purpose(models.TextChoices):
        IMPORT_SOURCE = "import_source", _("Arquivo de importação")
        EXPORT_RESULT = "export_result", _("Arquivo de exportação")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="document_files",
    )
    purpose = models.CharField(_("Finalidade"), max_length=30, choices=Purpose.choices)
    original_name = models.CharField(_("Nome original"), max_length=255)
    content_type = models.CharField(_("Tipo de conteúdo"), max_length=120, blank=True)
    size_bytes = models.PositiveBigIntegerField(_("Tamanho (bytes)"), default=0)
    file = models.FileField(_("Arquivo"), upload_to="transactions/files/%Y/%m/%d", blank=True)

    class Meta:
        """Model options intentionally explicit without schema-impacting settings."""

    def __str__(self) -> str:
        return self.original_name
