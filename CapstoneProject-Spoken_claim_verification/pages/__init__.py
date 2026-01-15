"""
Pages Package

Streamlit pages for the web interface.
"""

from . import home_page
from . import upload_page
from . import analysis_page
from . import results_page
from . import monitoring_page
from . import evaluation_page
from . import settings_page

__all__ = [
    "home_page",
    "upload_page",
    "analysis_page",
    "results_page",
    "monitoring_page",
    "evaluation_page",
    "settings_page",
]
