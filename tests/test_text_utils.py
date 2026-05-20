import unittest

from business_review_tool.text_utils import make_snippet, normalize_name, tokenize, top_terms


class TextUtilsTests(unittest.TestCase):
    def test_tokenize_removes_common_noise(self):
        tokens = tokenize("Great service and friendly staff at the cafe!")
        self.assertIn("service", tokens)
        self.assertIn("friendly", tokens)
        self.assertNotIn("and", tokens)

    def test_normalize_name_is_consistent(self):
        self.assertEqual(normalize_name("Helena Avenue Bakery"), "helena avenue bakery")

    def test_top_terms_extracts_themes(self):
        terms = top_terms(
            [
                "Friendly staff and quick service.",
                "Friendly team and quick service every time.",
                "Service was quick and the staff was kind.",
            ],
            top_n=3,
        )
        self.assertTrue(any("friendly" in term or "quick service" in term for term in terms))

    def test_make_snippet_truncates(self):
        text = "a" * 250
        self.assertTrue(make_snippet(text, max_len=50).endswith("..."))


if __name__ == "__main__":
    unittest.main()
