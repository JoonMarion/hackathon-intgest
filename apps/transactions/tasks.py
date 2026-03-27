from django.tasks import task

from apps.transactions.services.import_export import run_export_job, run_import_job


@task
def execute_import_job(*, import_job_id: int) -> dict[str, int | str]:
    return run_import_job(import_job_id=import_job_id)


@task
def generate_export_job(*, export_job_id: int) -> dict[str, int | str]:
    return run_export_job(export_job_id=export_job_id)
