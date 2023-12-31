import glob
import os
import subprocess
import tempfile
import unittest

import daikon_json


class TestFiles(unittest.TestCase):
    def test_output_equal(self):
        for infile_name in glob.glob("tests/*.json"):
            with self.subTest(input=infile_name):
                with open(infile_name) as infile:
                    # Build the Daikon input from the JSON
                    dtrace_file = tempfile.NamedTemporaryFile(
                        suffix=".dtrace", mode="w", delete=False
                    )
                    daikon_json.run_daikon(infile, dtrace_file)

                    # Run Daikon on the produced declarations and trace
                    jar_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "daikon.jar")
                    )
                    config_path = os.path.abspath(
                        os.path.join(os.path.dirname(__file__), "tests", "settings.txt")
                    )
                    invs_out = tempfile.NamedTemporaryFile(mode="w")
                    out = subprocess.run(
                        [
                            "java",
                            "-cp",
                            jar_path,
                            "daikon.Daikon",
                            "--config",
                            config_path,
                            "-o",
                            invs_out.name,
                            dtrace_file.name,
                        ],
                        capture_output=True,
                    )

                    # Remove the temporary files
                    os.remove(dtrace_file.name)

                    # Ensure Daikon did not exit with error
                    self.assertEqual(out.returncode, 0)

                    # Get the lines of the output from the delimiter ===
                    # skipping the next line which has the program point
                    # and excluding the last two lines which are info
                    lines = out.stdout.decode("utf-8").split("\n")
                    lines = lines[lines.index("=" * 75) + 2 : -2]

                    # Get the expected output and compare
                    with open(os.path.splitext(infile_name)[0] + ".invs") as outfile:
                        expected = set(map(str.strip, outfile.readlines()))
                    self.assertEqual(set(lines), expected)


if __name__ == "__main__":
    unittest.main()
