import json
from unittest.mock import patch

from apps.core.tests.base import BaseUnitTestCase
from apps.transactions.tasks import execute_import_job, generate_export_job


class TransactionTasksTests(BaseUnitTestCase):
    def test_task_functions_expose_enqueue(self):
        self.assertTrue(callable(execute_import_job.enqueue))
        self.assertTrue(callable(generate_export_job.enqueue))

    @patch("apps.transactions.tasks.run_import_job")
    def test_execute_import_job_returns_json_serializable_payload(self, run_import_job_mock):
        run_import_job_mock.return_value = {
            "status": "completed",
            "imported": 2,
            "skipped": 1,
            "failed": 0,
        }

        result = execute_import_job.func(import_job_id=11)

        run_import_job_mock.assert_called_once_with(import_job_id=11)
        self.assertEqual(result["status"], "completed")
        json.dumps(result)

    @patch("apps.transactions.tasks.run_export_job")
    def test_generate_export_job_returns_json_serializable_payload(self, run_export_job_mock):
        run_export_job_mock.return_value = {
            "status": "completed",
            "row_count": 3,
            "export_format": "xlsx",
        }

        result = generate_export_job.func(export_job_id=22)

        run_export_job_mock.assert_called_once_with(export_job_id=22)
        self.assertEqual(result["export_format"], "xlsx")
        json.dumps(result)
