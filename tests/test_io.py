from pathlib import Path
import tempfile
import unittest

from flowstate_equity.io import load_events


class IOTests(unittest.TestCase):
    def test_fixture_loads_and_ids_are_unique(self):
        rows = load_events("fixtures/work_events.csv")
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({row.event_id for row in rows}), 8)


    def test_duplicate_ids_are_rejected(self):
        source = Path("fixtures/work_events.csv").read_text()
        duplicate = source + source.splitlines()[1] + "\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicates.csv"
            path.write_text(duplicate)
            with self.assertRaisesRegex(ValueError, "unique"):
                load_events(path)


if __name__ == "__main__":
    unittest.main()

