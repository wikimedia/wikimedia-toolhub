# Copyright (c) 2020 Wikimedia Foundation and contributors.
# All Rights Reserved.
#
# This file is part of Toolhub.
#
# Toolhub is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Toolhub is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Toolhub.  If not, see <http://www.gnu.org/licenses/>.
from django.test import SimpleTestCase

from ..utils import LanguageData
from ..utils import language_data


class LanguageDataTest(SimpleTestCase):
    """Test LanguageData."""

    UNKNOWN_LANGUAGE_CODE = "xyz"

    def test_is_known(self):
        """Test is_known."""
        self.assertTrue(language_data.is_known("en"))
        self.assertFalse(language_data.is_known(self.UNKNOWN_LANGUAGE_CODE))

    def test_is_redirect(self):
        """Test is_redirect."""
        self.assertFalse(language_data.is_redirect("en"))
        self.assertEqual(language_data.is_redirect("aeb"), "aeb-arab")

    def test_get_script(self):
        """Test get_script."""
        self.assertEqual(language_data.get_script("en"), "Latn")
        self.assertEqual(
            language_data.get_script(self.UNKNOWN_LANGUAGE_CODE),
            LanguageData.UNKNOWN_SCRIPT,
        )

    def test_get_regions(self):
        """Test get_regions."""
        self.assertEqual(
            language_data.get_regions(self.UNKNOWN_LANGUAGE_CODE),
            [LanguageData.UNKNOWN_REGION],
        )
        self.assertEqual(language_data.get_regions("aeb"), ["AF"])

        en_regions = language_data.get_regions("en")
        self.assertIn("EU", en_regions)
        self.assertIn("AM", en_regions)
        self.assertIn("AS", en_regions)

    def test_get_autonym(self):
        """Test get_autonym."""
        self.assertEqual(
            language_data.get_autonym(self.UNKNOWN_LANGUAGE_CODE),
            LanguageData.UNKNOWN_AUTONYM,
        )
        self.assertEqual(language_data.get_autonym("aeb"), "تونسي")
        self.assertEqual(language_data.get_autonym("en"), "English")

    def test_get_autonyms(self):
        """Test get_autonyms."""
        autonyms = language_data.get_autonyms()
        self.assertEqual(autonyms["en"], "English")
        self.assertFalse(autonyms.get("aeb", False))

    def test_get_languages_in_scripts(self):
        """Test get_languages_in_scripts."""
        self.assertEqual(
            language_data.get_languages_in_scripts(
                [self.UNKNOWN_LANGUAGE_CODE]
            ),
            [],
        )
        langs = language_data.get_languages_in_scripts(["Latn", "Grek"])
        self.assertIn("zu", langs)
        self.assertIn("pnt", langs)
        self.assertNotIn("sr-el", langs)

    def test_get_group_of_script(self):
        """Test get_group_of_script."""
        self.assertEqual(language_data.get_group_of_script("Latn"), "Latin")
        self.assertEqual(
            language_data.get_group_of_script(self.UNKNOWN_LANGUAGE_CODE),
            LanguageData.OTHER_SCRIPT_GROUP,
        )

    def test_get_script_group_of_language(self):
        """Test get_script_group_of_language."""
        self.assertEqual(
            language_data.get_script_group_of_language(
                self.UNKNOWN_LANGUAGE_CODE
            ),
            LanguageData.OTHER_SCRIPT_GROUP,
        )
        self.assertEqual(
            language_data.get_script_group_of_language("en"), "Latin"
        )

    def test_get_languages_by_script_group(self):
        """Test get_languages_by_script_group."""
        actuals = language_data.get_languages_by_script_group(
            ["en", "sr-el", "tt-cyrl"],
        )
        self.assertIn("tt-cyrl", actuals["Cyrillic"])
        self.assertIn("en", actuals["Latin"])
        self.assertIn("sr-el", actuals["Latin"])

    def test_get_languages_by_script_group_in_regions(self):
        """Test get_languages_by_script_group_in_regions."""
        actuals = language_data.get_languages_by_script_group_in_regions(
            ["AS", "PA"],
        )
        self.assertIn("tpi", actuals["Latin"])
        self.assertIn("ug-arab", actuals["Arabic"])
        self.assertIn("zh-sg", actuals["CJK"])
        self.assertNotIn("axb", actuals["Arabic"])

    def test_sort_by_autonym(self):
        """Test sort_by_autonym."""
        codes = [
            "atj",
            "chr",
            "chy",
            "cr",
            "en",
            "es",
            "fr",
            "gn",
            "haw",
            "ike-cans",
            "ik",
            "kl",
            "nl",
            "pt",
            "qu",
            "srn",
            "yi",
            self.UNKNOWN_LANGUAGE_CODE,
        ]
        # NOTE: this does not exactly match the PHP utility's output.
        # PHP would place "chr" (Cherokee, autonym: ᏣᎳᎩ) before "ike-cans"
        # (Inuktitut, autonym: ᐃᓄᒃᑎᑐᑦ). Unicode sorting is hard y'all.
        self.assertEqual(
            language_data.sort_by_autonym(codes),
            [
                "atj",
                "gn",
                "en",
                "es",
                "fr",
                "haw",
                "ik",
                "kl",
                "nl",
                "pt",
                "qu",
                "srn",
                "chy",
                "yi",
                "ike-cans",
                "cr",
                "chr",
            ],
        )

    def test_sort_by_script_group(self):
        """Test sort_by_script_group."""
        codes = [
            "atj",
            "chr",
            "chy",
            "cr",
            "en",
            "es",
            "fr",
            "gn",
            "haw",
            "ike-cans",
            "ik",
            "kl",
            "nl",
            "pt",
            "qu",
            "srn",
            "yi",
            self.UNKNOWN_LANGUAGE_CODE,
        ]
        # NOTE: this does not exactly match the PHP utility's output.
        # PHP would place "chr" (Cherokee, autonym: ᏣᎳᎩ) before "ike-cans"
        # (Inuktitut, autonym: ᐃᓄᒃᑎᑐᑦ). Unicode sorting is hard y'all.
        self.assertEqual(
            language_data.sort_by_script_group(
                language_data.sort_by_autonym(codes)
            ),
            [
                "atj",
                "gn",
                "en",
                "es",
                "fr",
                "haw",
                "ik",
                "kl",
                "nl",
                "pt",
                "qu",
                "srn",
                "chy",
                "yi",
                "ike-cans",
                "cr",
                "chr",
            ],
        )

    def test_is_rtl(self):
        """Test is_rtl."""
        self.assertFalse(language_data.is_rtl("en"))
        self.assertFalse(language_data.is_rtl(self.UNKNOWN_LANGUAGE_CODE))
        self.assertTrue(language_data.is_rtl("he"))

    def test_get_dir(self):
        """Test get_dir."""
        self.assertEqual(LanguageData.DIR_LTR, language_data.get_dir("en"))
        self.assertEqual(LanguageData.DIR_RTL, language_data.get_dir("he"))
        self.assertFalse(language_data.get_dir(self.UNKNOWN_LANGUAGE_CODE))

    def test_get_languages_in_territory(self):
        """Test get_languages_in_territory."""
        at = language_data.get_languages_in_territory("AT")
        af = language_data.get_languages_in_territory("AF")

        self.assertIn("de", at)
        self.assertIn("bar", at)
        self.assertNotIn("he", at)

        self.assertIn("ug-arab", af)
        self.assertIn("tk", af)
        self.assertNotIn("de", af)

    def test_add_language(self):
        """Test add_language."""
        new_code = "bd808"
        self.assertFalse(language_data.is_known(new_code))
        self.assertNotIn(
            new_code,
            language_data.get_languages_by_script_group_in_region("AF")[
                "Latin"
            ],
        )
        language_data.add_language(
            new_code,
            {
                "script": "Latn",
                "regions": ["AF"],
                "autonym": "Test Language",
            },
        )
        self.assertTrue(language_data.is_known(new_code))
        self.assertIn(
            new_code,
            language_data.get_languages_by_script_group_in_region("AF")[
                "Latin"
            ],
        )
