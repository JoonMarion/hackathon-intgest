from functools import partial

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction as db_transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView, UpdateView
from django_filters.views import FilterView

from apps.categories.models import Category
from apps.transactions.http.filters import TransactionFilterSet
from apps.transactions.http.forms import TransactionForm, TransactionImportMappingForm, TransactionImportUploadForm
from apps.transactions.models import DocumentFile, ExportJob, ImportJob, Transaction
from apps.transactions.services import (
    build_filtered_summary,
    build_import_preview,
    extract_headers,
    resolve_selected_category_name,
)
from apps.transactions.tasks import execute_import_job, generate_export_job


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
        return Transaction.objects.filter(user=self.request.user).select_related("category", "account")

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
        context["export_filter_payload"] = {
            "q": current_filters["q"],
            "category": current_filters["category"],
            "kind": current_filters["kind"],
            "date_from": current_filters["date_from"],
            "date_to": current_filters["date_to"],
            "ordering": self.get_ordering_value(),
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
        label = transaction.payee.strip() if transaction.payee else transaction.description.strip()
        label = label or f"{transaction.get_kind_display()} {transaction.amount}"
        messages.success(self.request, f"Transação '{label}' removida com sucesso.")
        return super().form_valid(form)


class TransactionImportUploadView(LoginRequiredMixin, FormView):
    template_name = "transactions/pages/import_upload.html"
    form_class = TransactionImportUploadForm

    def form_valid(self, form):
        source_file = form.cleaned_data["source_file"]

        with db_transaction.atomic():
            document = DocumentFile.objects.create(
                user=self.request.user,
                purpose=DocumentFile.Purpose.IMPORT_SOURCE,
                original_name=source_file.name,
                content_type=getattr(source_file, "content_type", "") or "",
                size_bytes=source_file.size,
                file=source_file,
            )
            import_job = ImportJob.objects.create(
                user=self.request.user,
                source_file=document,
                status=ImportJob.Status.DRAFT,
            )

        try:
            headers = extract_headers(document)
        except ValueError:
            import_job.error_message = "Formato de arquivo não suportado para importação."
            import_job.status = ImportJob.Status.FAILED
            import_job.save(update_fields=["status", "error_message", "updated_at"])
            form.add_error("source_file", "Formato de arquivo não suportado.")
            return self.form_invalid(form)

        if not headers:
            import_job.error_message = "Nenhum cabeçalho foi identificado no arquivo."
            import_job.status = ImportJob.Status.FAILED
            import_job.save(update_fields=["status", "error_message", "updated_at"])
            form.add_error("source_file", "Não foi possível identificar cabeçalhos válidos.")
            return self.form_invalid(form)

        import_job.preview_summary = {"headers": headers}
        import_job.save(update_fields=["preview_summary", "updated_at"])

        messages.success(self.request, "Arquivo recebido. Defina o mapeamento para continuar.")
        return redirect("transactions_http:import_mapping", pk=import_job.pk)


class TransactionImportMappingView(LoginRequiredMixin, FormView):
    template_name = "transactions/pages/import_mapping.html"
    form_class = TransactionImportMappingForm

    def dispatch(self, request, *args, **kwargs):
        self.import_job = get_object_or_404(ImportJob, pk=kwargs["pk"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_headers(self) -> list[str]:
        headers = self.import_job.preview_summary.get("headers", [])
        if headers:
            return headers

        headers = extract_headers(self.import_job.source_file)
        preview_summary = dict(self.import_job.preview_summary)
        preview_summary["headers"] = headers
        self.import_job.preview_summary = preview_summary
        self.import_job.save(update_fields=["preview_summary", "updated_at"])
        return headers

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["headers"] = self.get_headers()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["import_job"] = self.import_job
        context["headers"] = self.get_headers()
        return context

    def form_valid(self, form):
        mapping = form.cleaned_data
        try:
            summary, rows = build_import_preview(import_job=self.import_job, mapping=mapping)
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

        self.import_job.column_mapping = mapping
        self.import_job.preview_summary = {**summary, "headers": self.get_headers()}
        self.import_job.preview_rows = rows
        self.import_job.save(update_fields=["column_mapping", "preview_summary", "preview_rows", "updated_at"])

        messages.success(self.request, "Preview gerado. Revise os resultados por linha antes de confirmar.")
        return redirect("transactions_http:import_preview", pk=self.import_job.pk)


class TransactionImportPreviewView(LoginRequiredMixin, DetailView):
    model = ImportJob
    template_name = "transactions/pages/import_preview.html"
    context_object_name = "import_job"

    def get_queryset(self):
        return ImportJob.objects.filter(user=self.request.user).select_related("source_file")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import_job = self.object
        summary = dict(import_job.preview_summary)
        rows = list(import_job.preview_rows)
        context["preview_summary"] = summary
        context["preview_rows"] = rows
        return context


class TransactionImportConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        import_job = get_object_or_404(ImportJob, pk=pk, user=request.user)

        if not import_job.column_mapping:
            messages.error(request, "Mapeie as colunas antes de confirmar a importação.")
            return redirect("transactions_http:import_mapping", pk=import_job.pk)

        with db_transaction.atomic():
            import_job.status = ImportJob.Status.QUEUED
            import_job.error_message = ""
            import_job.save(update_fields=["status", "error_message", "updated_at"])
            db_transaction.on_commit(partial(execute_import_job.enqueue, import_job_id=import_job.pk))

        messages.success(request, "Importação confirmada. O processamento foi iniciado.")
        return redirect("transactions_http:import_status", pk=import_job.pk)


class TransactionImportStatusView(LoginRequiredMixin, DetailView):
    model = ImportJob
    template_name = "transactions/pages/import_status.html"
    context_object_name = "import_job"

    def get_queryset(self):
        return ImportJob.objects.filter(user=self.request.user).select_related("source_file")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import_job = self.object
        context["rows"] = import_job.rows.select_related("transaction").order_by("row_number")[:300]
        return context


class TransactionExportCreateView(LoginRequiredMixin, View):
    EXPORT_FILTER_KEYS = ("q", "category", "kind", "date_from", "date_to", "ordering")

    def post(self, request):
        export_format = request.POST.get("format", ExportJob.Format.CSV)
        if export_format not in {ExportJob.Format.CSV, ExportJob.Format.XLSX}:
            messages.error(request, "Formato de exportação inválido.")
            return redirect("transactions_http:index")

        filters = {key: request.POST.get(key, "") for key in self.EXPORT_FILTER_KEYS}

        extension = "csv" if export_format == ExportJob.Format.CSV else "xlsx"
        mime_type = "text/csv" if extension == "csv" else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        with db_transaction.atomic():
            output_file = DocumentFile.objects.create(
                user=request.user,
                purpose=DocumentFile.Purpose.EXPORT_RESULT,
                original_name=f"transactions-export.{extension}",
                content_type=mime_type,
                size_bytes=0,
            )
            export_job = ExportJob.objects.create(
                user=request.user,
                output_file=output_file,
                status=ExportJob.Status.QUEUED,
                export_format=export_format,
                filters=filters,
            )
            db_transaction.on_commit(partial(generate_export_job.enqueue, export_job_id=export_job.pk))

        messages.success(request, "Exportação iniciada. O arquivo será gerado em segundo plano.")
        return redirect("transactions_http:export_status", pk=export_job.pk)


class TransactionExportStatusView(LoginRequiredMixin, DetailView):
    model = ExportJob
    template_name = "transactions/pages/export_status.html"
    context_object_name = "export_job"

    def get_queryset(self):
        return ExportJob.objects.filter(user=self.request.user).select_related("output_file")


class TransactionExportDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        export_job = get_object_or_404(
            ExportJob.objects.select_related("output_file"),
            pk=pk,
            user=request.user,
        )
        output_file = export_job.output_file

        if export_job.status != ExportJob.Status.COMPLETED or not output_file.file:
            messages.error(request, "O arquivo ainda não está pronto para download.")
            return redirect("transactions_http:export_status", pk=export_job.pk)

        file_name = output_file.original_name or output_file.file.name.rsplit("/", maxsplit=1)[-1]
        if not output_file.file.storage.exists(output_file.file.name):
            raise Http404("Arquivo não encontrado.")

        return FileResponse(
            output_file.file.open("rb"),
            as_attachment=True,
            filename=file_name,
            content_type=output_file.content_type or "application/octet-stream",
        )

