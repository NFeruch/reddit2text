"""Tests for Reddit2Text init, multi-URL, save_output, and shared behavior."""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from reddit2text.main import Reddit2Text


@pytest.fixture
def r2t():
    """Reddit2Text instance with dummy credentials (not used under patch)."""
    return Reddit2Text(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
    )


class TestInit:
    """Constructor and credentials."""

    def test_raises_when_credentials_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with patch("reddit2text.main.os.getenv", return_value=None):
                with pytest.raises(ValueError, match="client_id|Please provide"):
                    Reddit2Text()

    def test_raises_when_only_some_credentials_given(self) -> None:
        with patch("reddit2text.main.os.getenv", return_value=None):
            with pytest.raises(ValueError):
                Reddit2Text(client_id="id", client_secret="secret")

    def test_accepts_explicit_credentials(self) -> None:
        r = Reddit2Text(
            client_id="id",
            client_secret="secret",
            user_agent="ua",
        )
        assert r.client_id == "id"
        assert r.client_secret == "secret"
        assert r.user_agent == "ua"

    def test_default_format_is_txt(self) -> None:
        r = Reddit2Text(
            client_id="id",
            client_secret="secret",
            user_agent="ua",
        )
        assert r.format == "txt"

    def test_default_comment_delim(self) -> None:
        r = Reddit2Text(
            client_id="id",
            client_secret="secret",
            user_agent="ua",
        )
        assert r.comment_delim == "|"

    def test_save_output_to_default_none(self) -> None:
        r = Reddit2Text(
            client_id="id",
            client_secret="secret",
            user_agent="ua",
        )
        assert r.save_output_to is None


class TestMultiUrl:
    """Multiple URLs return list; single URL returns str."""

    def test_single_url_returns_string(
        self, r2t: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t.textualize_post("https://reddit.com/r/fake/comments/abc123/")
        assert isinstance(out, str)
        assert "Sample post title" in out

    def test_multiple_urls_return_list(
        self, r2t: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t.textualize_post(
                [
                    "https://reddit.com/r/fake/comments/abc123/",
                    "https://reddit.com/r/fake/comments/def456/",
                ]
            )
        assert isinstance(out, list)
        assert len(out) == 2
        assert all(isinstance(s, str) for s in out)
        assert "Sample post title" in out[0]
        assert "Sample post title" in out[1]


class TestSaveOutputTo:
    """save_output_to writes output to file."""

    def test_writes_to_file_when_save_output_to_set(
        self, r2t: Reddit2Text, fake_submission: Any, tmp_path: Path
    ) -> None:
        out_path = tmp_path / "out.txt"
        r2t.save_output_to = str(out_path)
        with patch.object(r2t, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            r2t.textualize_post("https://reddit.com/r/fake/comments/abc123/")
        assert out_path.exists()
        content = out_path.read_text()
        assert "Sample post title" in content

    def test_single_url_still_returns_string_when_saving(
        self, r2t: Reddit2Text, fake_submission: Any, tmp_path: Path
    ) -> None:
        r2t.save_output_to = str(tmp_path / "out.txt")
        with patch.object(r2t, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t.textualize_post("https://reddit.com/r/fake/comments/abc123/")
        assert isinstance(out, str)
