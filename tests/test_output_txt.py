"""Tests for plain-text (txt) output format."""

from typing import Any
from unittest.mock import patch

import pytest

from reddit2text.main import Reddit2Text


@pytest.fixture
def r2t_txt():
    """Reddit2Text with txt format (default)."""
    return Reddit2Text(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
        format="txt",
    )


class TestTxtContent:
    """Content and structure of txt output."""

    def test_includes_post_title_author_upvotes_body(
        self, r2t_txt: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert "Sample post title" in out
        assert "test_user" in out
        assert "42" in out
        assert "This is the post body." in out

    def test_includes_top_level_and_nested_comments(
        self, r2t_txt: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert "commenter_one" in out
        assert "First top-level comment." in out
        assert "commenter_two" in out
        assert "A reply to the first comment." in out
        assert "[deleted]" in out
        assert "Deleted user comment." in out

    def test_deleted_author_shown_as_bracket_deleted(
        self, r2t_txt: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert "[deleted]" in out


class TestTxtCommentDepth:
    """max_comment_depth behavior for txt."""

    def test_respects_max_comment_depth(
        self, r2t_txt: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_txt.max_comment_depth = 1
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert "First top-level comment." in out
        assert "A reply to the first comment." not in out

    def test_depth_zero_returns_only_post_no_comment_section(
        self, r2t_txt: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_txt.max_comment_depth = 0
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert "Sample post title" in out
        assert "Comments:" not in out
        assert "commenter_one" not in out


class TestTxtCommentDelimiter:
    """comment_delim affects txt indentation."""

    def test_custom_delimiter_appears_in_output(
        self, r2t_txt: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_txt.comment_delim = ">>>"
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert ">>>" in out
        assert "commenter_one" in out


class TestTxtEdgeCases:
    """Edge cases: no selftext, no comments."""

    def test_post_without_body_no_body_line(
        self, r2t_txt: Reddit2Text, minimal_fake_submission: Any
    ) -> None:
        with patch.object(r2t_txt, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = minimal_fake_submission
            out = r2t_txt.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert "Title only" in out
        assert "op" in out
        assert "Body text:" not in out
        assert "0 Comments:" in out or "Comments:" in out
