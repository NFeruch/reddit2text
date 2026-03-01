"""Tests for CSV output format."""

import csv
import io
from typing import Any
from unittest.mock import patch

import pytest

from reddit2text.main import Reddit2Text


@pytest.fixture
def r2t_csv():
    """Reddit2Text with csv format."""
    return Reddit2Text(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
        format="csv",
    )


class TestCsvStructure:
    """Header and row count."""

    def test_output_is_string(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert isinstance(out, str)

    def test_header_row(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        assert rows[0] == ["depth", "author", "score", "body"]


class TestCsvPostRow:
    """First data row is the post."""

    def test_post_as_depth_zero_row(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        assert rows[1][0] == "0"
        assert rows[1][1] == "test_user"
        assert "Sample post title" in rows[1][3]
        assert "This is the post body." in rows[1][3]


class TestCsvCommentRows:
    """Comment rows: depth, author, score, body."""

    def test_first_comment_row(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        assert rows[2][0] == "1"
        assert rows[2][1] == "commenter_one"
        assert rows[2][3] == "First top-level comment."

    def test_reply_has_depth_two(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        # Row 3 = first reply (depth 2)
        assert rows[3][0] == "2"
        assert rows[3][1] == "commenter_two"
        assert rows[3][3] == "A reply to the first comment."

    def test_deleted_author_row(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        # Last comment row is [deleted]
        assert any(r[1] == "[deleted]" for r in rows[1:])


class TestCsvCommentDepth:
    """max_comment_depth for CSV."""

    def test_respects_max_comment_depth(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_csv.max_comment_depth = 1
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        # Header + post + 2 top-level comments only (no reply)
        assert len(rows) == 4
        bodies = [r[3] for r in rows[1:]]
        assert "A reply to the first comment." not in bodies

    def test_depth_zero_only_header_and_post(
        self, r2t_csv: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_csv.max_comment_depth = 0
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        assert len(rows) == 2
        assert rows[0] == ["depth", "author", "score", "body"]
        assert rows[1][1] == "test_user"


class TestCsvEdgeCases:
    """Minimal thread: no selftext, no comments."""

    def test_minimal_thread_two_rows(
        self, r2t_csv: Reddit2Text, minimal_fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = minimal_fake_submission
            out = r2t_csv.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        assert len(rows) == 2
        assert rows[1][0] == "0"
        assert rows[1][1] == "op"
        assert "Title only" in rows[1][3]


@pytest.fixture
def r2t_csv_relational():
    """Reddit2Text with csv_relational format."""
    return Reddit2Text(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
        format="csv_relational",
    )


class TestCsvRelational:
    """Two-table relational CSV: posts + comments with IDs for joining."""

    def test_returns_posts_csv(
        self, r2t_csv_relational: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_csv_relational, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_csv_relational.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        rows = list(csv.reader(io.StringIO(out)))
        assert rows[0] == [
            "post_id",
            "title",
            "author",
            "upvotes",
            "selftext",
            "num_comments",
        ]
        assert len(rows) == 2
        assert rows[1][0] == "post"
        assert rows[1][1] == "Sample post title"
        assert rows[1][2] == "test_user"

    def test_comments_have_ids_and_parent_id(
        self, r2t_csv_relational: Reddit2Text, fake_submission: Any, tmp_path
    ) -> None:
        r2t_csv_relational.save_output_to = str(tmp_path / "out.csv")
        with patch.object(r2t_csv_relational, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            r2t_csv_relational.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert (tmp_path / "out_posts.csv").exists()
        comments_path = tmp_path / "out_comments.csv"
        assert comments_path.exists()
        rows = list(csv.reader(io.StringIO(comments_path.read_text())))
        assert rows[0] == [
            "comment_id",
            "post_id",
            "parent_id",
            "depth",
            "author",
            "score",
            "body",
        ]
        # Top-level: parent_id = post
        assert rows[1][0] == "c0"
        assert rows[1][1] == "post"
        assert rows[1][2] == "post"
        assert rows[1][3] == "1"
        assert rows[1][6] == "First top-level comment."
        # Reply: parent_id = c0
        assert rows[2][0] == "c0_0"
        assert rows[2][2] == "c0"
        assert rows[2][6] == "A reply to the first comment."

    def test_writes_two_files_when_save_output_to_set(
        self, r2t_csv_relational: Reddit2Text, fake_submission: Any, tmp_path
    ) -> None:
        r2t_csv_relational.save_output_to = str(tmp_path / "thread.csv")
        with patch.object(r2t_csv_relational, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            r2t_csv_relational.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert (tmp_path / "thread_posts.csv").exists()
        assert (tmp_path / "thread_comments.csv").exists()
        posts = (tmp_path / "thread_posts.csv").read_text()
        assert "post_id" in posts and "Sample post title" in posts
        comments = (tmp_path / "thread_comments.csv").read_text()
        assert "comment_id" in comments and "parent_id" in comments
