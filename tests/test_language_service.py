import unittest

from src.language_service import get_crop_description, get_label


class TestLanguageService(unittest.TestCase):
    def test_core_ui_labels_are_available_in_all_supported_languages(self):
        for key in ("select_language", "save_profile", "suggested_questions", "market_guidance"):
            for language in ("en", "ta", "te", "hi"):
                with self.subTest(key=key, language=language):
                    self.assertTrue(get_label(key, language))

    def test_crop_descriptions_are_translated_for_supported_locations(self):
        crop = {
            "id": "rice",
            "description": "English source description.",
        }
        self.assertNotEqual(get_crop_description(crop, "ta"), crop["description"])
        self.assertNotEqual(get_crop_description(crop, "te"), crop["description"])
        self.assertNotEqual(get_crop_description(crop, "hi"), crop["description"])

    def test_missing_crop_translation_falls_back_to_source_english(self):
        crop = {"id": "untranslated_crop", "description": "English source description."}
        self.assertEqual(get_crop_description(crop, "ta"), crop["description"])


if __name__ == "__main__":
    unittest.main()
