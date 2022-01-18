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
"""Configuration for Sphinx documentation generation."""
import datetime
import os
import sys

import django

import sphinx_rtd_theme


DOC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DOC_DIR)
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "toolhub.settings")
django.setup()


extensions = [
    "sphinx_copybutton",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinxcontrib_django",
]


intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/2.2/",
        "https://docs.djangoproject.com/en/2.2/_objects/",
    ),
}


templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "Toolhub"
copyright = "{}, Wikimedia Foundation & contributors".format(
    datetime.date.today().year
)
version = "0.1"
release = version

exclude_patterns = ["_build"]
pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]
htmlhelp_basename = "Toolhubdoc"

autodoc_default_flags = ["members", "private-members", "special-members"]
autodoc_memeber_order = "groupwise"

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
