"""Tests for Task 1: project scaffold structure and app.py shell."""
import importlib
import os
import sys


def test_requirements_txt_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    assert os.path.isfile(path), "requirements.txt must exist in dashboard/"


def test_requirements_contains_core_deps():
    path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    content = open(path).read()
    for dep in ["streamlit", "snowflake-connector-python", "pandas", "plotly", "python-dotenv"]:
        assert dep in content, f"requirements.txt must list {dep}"


def test_env_example_exists():
    path = os.path.join(os.path.dirname(__file__), "..", ".env.example")
    assert os.path.isfile(path), ".env.example must exist in dashboard/"


def test_env_example_documents_required_vars():
    path = os.path.join(os.path.dirname(__file__), "..", ".env.example")
    content = open(path).read()
    for var in [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_ROLE",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA",
        "SNOWFLAKE_PRIVATE_KEY_PATH",
        "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE",
    ]:
        assert var in content, f".env.example must document {var}"


def test_app_py_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "app.py")
    assert os.path.isfile(path), "app.py must exist in dashboard/"


def test_sections_package_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "sections", "__init__.py")
    assert os.path.isfile(path), "dashboard/sections/__init__.py must exist"


def test_section_modules_exist():
    base = os.path.join(os.path.dirname(__file__), "..", "sections")
    for name in ["overview", "sales", "customers", "sellers"]:
        path = os.path.join(base, f"{name}.py")
        assert os.path.isfile(path), f"sections/{name}.py must exist"


def test_section_modules_have_render():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    for name in ["overview", "sales", "customers", "sellers"]:
        mod = importlib.import_module(f"sections.{name}")
        assert hasattr(mod, "render"), f"sections/{name}.py must expose a render() function"
