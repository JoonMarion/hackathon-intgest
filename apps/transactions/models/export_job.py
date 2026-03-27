from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.models import BaseModel


class ExportJob(BaseModel):
    class Status(models.TextChoices):
        QUEUED = "queued", _("Na fila")
        PROCESSING = "processing", _("Processando")
        COMPLETED = "completed", _("Concluído")
        FAILED = "failed", _("Falhou")

    class Format(models.TextChoices):
        CSV = "csv", "CSV"
        XLSX = "xlsx", "XLSX"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="export_jobs",
    )
    output_file = models.ForeignKey(
        "transactions.DocumentFile",
        verbose_name=_("Arquivo gerado"),
        on_delete=models.PROTECT,
        related_name="export_jobs",
    )
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.QUEUED)
    export_format = models.CharField(_("Formato"), max_length=10, choices=Format.choices)
    filters = models.JSONField(_("Filtros"), default=dict, blank=True)
    row_count = models.PositiveIntegerField(_("Quantidade de linhas"), default=0)
    error_message = models.TextField(_("Erro"), blank=True)

    class Meta:
        """Model options intentionally explicit without schema-impacting settings."""
