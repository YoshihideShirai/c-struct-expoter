import unittest
import os
from main import load_target_structs
from clang.cindex import Index, CursorKind, TokenKind
from main import reconstruct_macro


class TestLoadTargetStructs(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.test_file = "test_structs.txt"
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("StructA\n")
            f.write("StructB\n")
            f.write("\n")  # Empty line
            f.write("StructC\n")

    def tearDown(self):
        # Remove the temporary file after tests
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_target_structs(self):
        # Test if the function correctly loads struct names
        expected = {"StructA", "StructB", "StructC"}
        result = load_target_structs(self.test_file)
        self.assertEqual(result, expected)

    def test_load_target_structs_empty_file(self):
        # Test with an empty file
        empty_file = "empty_structs.txt"
        with open(empty_file, "w", encoding="utf-8") as f:
            pass
        try:
            result = load_target_structs(empty_file)
            self.assertEqual(result, set())
        finally:
            os.remove(empty_file)


if __name__ == "__main__":
    unittest.main()
