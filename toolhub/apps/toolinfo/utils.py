# Copyright (c) 2021 Wikimedia Foundation and contributors.
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
# Copyright (c) 2021 Wikimedia Foundation and contributors.
# All Rights Reserved.
import json
import locale
import os
from collections import defaultdict


class LanguageData:  # noqa: R0904 Too many public methods
    """Helper for working with language-data.json.

    This class is largely a port of
    https://github.com/wikimedia/language-data/blob/master/src/index.js to
    python.
    """

    UNKNOWN_SCRIPT = False
    UNKNOWN_REGION = "UNKNOWN"
    UNKNOWN_AUTONYM = False
    OTHER_SCRIPT_GROUP = "Other"
    DIR_RTL = "rtl"
    DIR_LTR = "ltr"

    def __init__(self):
        """Initialize instance."""
        # FIXME: this data file needs to be updated periodically and right now
        # we have nothing to remind us to do that. This class really should be
        # upstreamed to https://github.com/wikimedia/language-data so that we
        # can just depend on an upstream project.
        data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data",
            "language-data.json",
        )
        with open(data_path) as fh:
            self.data = json.load(fh)

    def is_known(self, language):
        """Is the language known?"""
        return language in self.data["languages"]

    def is_redirect(self, language):
        """Is this language a redirect to another language?"""
        if (
            self.is_known(language)
            and len(self.data["languages"][language]) == 1
        ):
            return self.data["languages"][language][0]
        return False

    def get_languages(self):
        """Get all the languages."""
        return self.data["languages"]

    def get_script(self, language):
        """Returns the script of the language."""
        target = self.is_redirect(language)
        if target:
            return self.get_script(target)
        if not self.is_known(language):
            return self.UNKNOWN_SCRIPT
        return self.data["languages"][language][0]

    def get_regions(self, language):
        """Returns the regions in which a language is spoken."""
        target = self.is_redirect(language)
        if target:
            return self.get_regions(target)
        if self.is_known(language):
            return self.data["languages"][language][1]
        return [self.UNKNOWN_REGION]

    def get_autonym(self, language):
        """Returns the autonym of the language."""
        target = self.is_redirect(language)
        if target:
            return self.get_autonym(target)
        if self.is_known(language):
            return self.data["languages"][language][2]
        return self.UNKNOWN_AUTONYM

    def only_languages(self):
        """Generator over non-redirect languages."""
        for language in self.data["languages"]:
            if not self.is_redirect(language):
                yield language

    def get_autonyms(self):
        """Returns all language codes and corresponding autonyms."""
        return {
            language: self.get_autonym(language)
            for language in self.only_languages()
        }

    def get_languages_in_scripts(self, scripts):
        """Returns all languages written in the given scripts."""
        return [
            language
            for language in self.only_languages()
            if self.get_script(language) in scripts
        ]

    def get_languages_in_script(self, script):
        """Returns all languages written in script."""
        return self.get_languages_in_scripts([script])

    def get_group_of_script(self, script):
        """Returns the script group of a script."""
        for name, group in self.data["scriptgroups"].items():
            if script in group:
                return name
        return self.OTHER_SCRIPT_GROUP

    def get_script_group_of_language(self, language):
        """Returns the script group of a language."""
        return self.get_group_of_script(self.get_script(language))

    def get_languages_by_script_group(self, languages):
        """Get the given list of languages grouped by script."""
        by_group = defaultdict(list)
        for language in languages:
            resolved = self.is_redirect(language) or language
            group = self.get_script_group_of_language(resolved)
            by_group[group].append(language)
        return by_group

    def get_languages_by_script_group_in_regions(self, regions):
        """Returns a dict of languages grouped by script group."""
        by_group = defaultdict(list)
        for language in self.only_languages():
            lang_regions = self.get_regions(language)
            group = self.get_script_group_of_language(language)
            for region in regions:
                if region in lang_regions:
                    by_group[group].append(language)
        return by_group

    def get_languages_by_script_group_in_region(self, region):
        """Returns a dict of languages grouped by script group."""
        return self.get_languages_by_script_group_in_regions([region])

    def sort_by_script_group(self, languages):
        """Return the list of languages sorted by script groups."""
        ret = []
        grouped = self.get_languages_by_script_group(languages)
        for group in sorted(grouped.keys()):
            ret = ret + grouped[group]
        return ret

    def sort_by_autonym(self, languages):
        """Sort a list of languages by their autonyms."""
        return sorted(
            (lang for lang in languages if self.get_autonym(lang)),
            key=lambda x: locale.strxfrm((self.get_autonym(x) or x).lower()),
        )

    def is_rtl(self, language):
        """Check if a language is right-to-left."""
        return self.get_script(language) in self.data["rtlscripts"]

    def get_dir(self, language):
        """Return the direction of the language."""
        if self.is_known(language):
            if self.is_rtl(language):
                return self.DIR_RTL
            return self.DIR_LTR
        return False

    def get_languages_in_territory(self, territory):
        """Returns the languages spoken in a territory."""
        return self.data["territories"].get(territory, [])

    def add_language(self, code, options):
        """Adds a language in run time and sets its options as provided.

        If the target option is provided, the language is defined as
        a redirect. Other possible options are script, regions and autonym.
        """
        if "target" in options:
            self.data["languages"][code] = [options["target"]]
        else:
            self.data["languages"][code] = [
                options.get("script", "Latn"),
                options.get("regions", []),
                options.get("autonym", code),
            ]


language_data = LanguageData()
