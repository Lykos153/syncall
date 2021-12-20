from unittest.mock import patch

import pytest

from taskwarrior_syncall import (
    cache_or_reuse_cached_combination,
    fetch_app_configuration,
    inform_about_combination_name_usage,
    list_named_configs,
    report_toplevel_exception,
)


def test_list_named_configs(fs, caplog, mock_prefs_manager):
    with patch(
        "taskwarrior_syncall.app_utils.PrefsManager",
        return_value=mock_prefs_manager,
    ):
        list_named_configs("doesnt matter")
        captured = caplog.text
        assert all(
            expected_config in captured
            for expected_config in (
                "kalimera",
                "kalinuxta",
                "kalispera",
            )
        )


def test_fetch_app_configuration(fs, caplog, mock_prefs_manager):
    with patch("taskwarrior_syncall.app_utils.PrefsManager", return_value=mock_prefs_manager):
        # invalid combination
        config = fetch_app_configuration(config_fname="doesntmatter", combination="kalimera")
        config.keys() == ["a", "b", "c"]
        config.values() == [1, 2, [1, 2, 3]]
        captured = caplog.text
        assert "Loading configuration" in captured

        # invalid combination
        caplog.clear()
        with pytest.raises(RuntimeError):
            fetch_app_configuration(config_fname="doesntmatter", combination="doesntexist")
            captured = caplog.text
            assert "No such configuration" in captured


def test_report_toplevel_exception(caplog):
    report_toplevel_exception()
    assert "bergercookie/taskwarrior_syncall" in caplog.text


def test_inform_about_combination_name_usage(fs, caplog):
    e = "kalimera"
    c = "kalinuxta"
    inform_about_combination_name_usage(exec_name=e, combination_name=c)
    assert e in caplog.text and c in caplog.text


def test_cache_or_reuse_cached_combination(fs, caplog, mock_prefs_manager):
    with patch("taskwarrior_syncall.app_utils.PrefsManager", return_value=mock_prefs_manager):
        cache_or_reuse_cached_combination(
            config_args={"a": 1, "b": 2, "c": 3},
            config_fname="TBD",
            custom_combination_savename=None,
        )

        assert "Caching this configuration" in caplog.text
        caplog.clear()

        cache_or_reuse_cached_combination(
            config_args={"a": 1, "b": 2, "c": 3},
            config_fname="kalimera",
            custom_combination_savename=None,
        )

        assert "Loading cached configuration" in caplog.text and "1__2__3" in caplog.text
        caplog.clear()