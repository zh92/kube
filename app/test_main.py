"""Focused tests for file persistence in main.py (stdlib unittest)."""

import json
import tempfile
import unittest
from pathlib import Path

import main


class PersistenceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.real_data_file = main.DATA_FILE
        self.real_tasks = main.tasks
        main.DATA_FILE = Path(self.tmp.name) / "tasks.json"
        main.tasks = []

    def tearDown(self):
        main.DATA_FILE = self.real_data_file
        main.tasks = self.real_tasks
        self.tmp.cleanup()

    def test_missing_file_loads_empty(self):
        self.assertEqual(main.load_tasks(), [])

    def test_save_then_load_round_trip(self):
        main.tasks = [{"id": 1, "title": "t", "status": "doing"}]
        main.save_tasks()
        self.assertEqual(
            main.load_tasks(), [{"id": 1, "title": "t", "status": "doing"}]
        )

    def test_save_leaves_no_temp_file(self):
        main.tasks = [{"id": 1, "title": "t", "status": "todo"}]
        main.save_tasks()
        leftovers = list(Path(self.tmp.name).glob("*.tmp"))
        self.assertEqual(leftovers, [])

    def test_corrupt_file_fails_loud(self):
        main.DATA_FILE.write_text("{not json")
        with self.assertRaises(json.JSONDecodeError):
            main.load_tasks()


if __name__ == "__main__":
    unittest.main()
