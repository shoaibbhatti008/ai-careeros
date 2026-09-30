"""Tests for the environment variable loader."""

import os

import pytest

from config.env import Env, EnvError  # pyright: ignore[reportMissingImports]


def test_env_reads_string(monkeypatch: pytest.MonkeyPatch) -> None:
    """env() should return string values."""
    monkeypatch.setenv("TEST_STRING", "hello")
    env = Env()
    assert env("TEST_STRING") == "hello"


def test_env_raises_on_missing_required() -> None:
    """env() should raise EnvError for missing required vars."""
    env = Env()
    os.environ.pop("DEFINITELY_MISSING_VAR_12345", None)
    with pytest.raises(EnvError):
        env("DEFINITELY_MISSING_VAR_12345")


def test_env_bool_true_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """env.bool() should parse truthy values."""
    env = Env()
    for value in ("true", "True", "TRUE", "1", "yes", "on"):
        monkeypatch.setenv("TEST_BOOL", value)
        assert env.bool("TEST_BOOL") is True


def test_env_bool_false_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """env.bool() should parse falsy values."""
    env = Env()
    for value in ("false", "False", "0", "no", "off"):
        monkeypatch.setenv("TEST_BOOL", value)
        assert env.bool("TEST_BOOL") is False


def test_env_int(monkeypatch: pytest.MonkeyPatch) -> None:
    """env.int() should parse integers."""
    monkeypatch.setenv("TEST_INT", "42")
    env = Env()
    assert env.int("TEST_INT") == 42


def test_env_int_raises_on_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    """env.int() should raise EnvError on invalid integer."""
    monkeypatch.setenv("TEST_INT", "not-a-number")
    env = Env()
    with pytest.raises(EnvError):
        env.int("TEST_INT")


def test_env_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """env.list() should parse comma-separated values."""
    monkeypatch.setenv("TEST_LIST", "a,b,c")
    env = Env()
    assert env.list("TEST_LIST") == ["a", "b", "c"]


def test_env_list_handles_spaces(monkeypatch: pytest.MonkeyPatch) -> None:
    """env.list() should trim whitespace."""
    monkeypatch.setenv("TEST_LIST", "a, b , c ")
    env = Env()
    assert env.list("TEST_LIST") == ["a", "b", "c"]


def test_env_default_values(monkeypatch: pytest.MonkeyPatch) -> None:
    """env() with default should not raise."""
    monkeypatch.delenv("TEST_DEFAULT", raising=False)
    env = Env()
    assert env("TEST_DEFAULT", default="fallback") == "fallback"