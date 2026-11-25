import io
import unittest
from contextlib import redirect_stdout

import bhashapy_lang as bp


class TestBhashaPy(unittest.TestCase):
    def test_translate_to_python_keywords(self):
        src = (
            'vidhi jodo_do(a, b):\n'
            '    yadi a > b:\n'
            '        bhejo a\n'
            '    nahi_toh:\n'
            '        bhejo b\n'
        )
        expected = (
            'def jodo_do(a, b):\n'
            '    if a > b:\n'
            '        return a\n'
            '    else:\n'
            '        return b\n'
        )
        self.assertEqual(bp.translate_to_python(src), expected)

    def test_attribute_access_not_translated(self):
        src = 'likho(obj.yadi)\n'
        self.assertEqual(bp.translate_to_python(src), 'print(obj.yadi)\n')

    def test_reverse_translate_to_bhasha(self):
        py_src = 'for i in range(3):\n    print(i)\n'
        expected = 'pratyek i andar kram(3):\n    likho(i)\n'
        self.assertEqual(bp.translate_to_bhasha(py_src), expected)

    def test_analyze_code_valid(self):
        src = 'pratyek i andar kram(1, 3):\n    likho(i)\n'
        stats = bp.analyze_code(src)
        self.assertTrue(stats["valid"])
        self.assertEqual(stats["non_empty_lines"], 2)
        self.assertEqual(stats["bhasha_keywords_used"], 4)

    def test_builtins_and_execution(self):
        src = (
            'items = taalika(kram(1, 5))\n'
            'total = kul(items)\n'
            'rev = palti("abc")\n'
            'picked = chuno(["x", "y"])\n'
        )
        env = bp.create_env()
        exec(compile(bp.translate_to_python(src), "<test>", "exec"), env)
        self.assertEqual(env["items"], [1, 2, 3, 4])
        self.assertEqual(env["total"], 10)
        self.assertEqual(env["rev"], "cba")
        self.assertIn(env["picked"], ["x", "y"])

    def test_dabba_and_dinank(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            boxed = bp._builtin_dabba("Namaste")
        self.assertIn("+---------+", boxed)
        self.assertIn("| Namaste |", boxed)
        self.assertIn(",", bp._builtin_dinank())

    def test_typo_suggestion_in_name_error(self):
        err = NameError("name 'liko' is not defined")
        err.name = "liko"
        formatted = bp.format_hinglish_error(err, source_name="test.bhasha")
        self.assertIn("likho", formatted)
        self.assertIn("[Truti", formatted)


if __name__ == "__main__":
    unittest.main()
