"""Tests for JSON output format."""

import json
from typing import Any
from unittest.mock import patch

import pytest

from reddit2text.main import Reddit2Text


@pytest.fixture
def r2t_json():
    """Reddit2Text with json format."""
    return Reddit2Text(
        client_id="test_id",
        client_secret="test_secret",
        user_agent="test_agent",
        format="json",
    )


class TestJsonStructure:
    """Top-level keys and types."""

    def test_output_is_valid_json_string(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        assert isinstance(out, str)
        data = json.loads(out)
        assert isinstance(data, dict)

    def test_has_post_and_comments_keys(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        assert "post" in data
        assert "comments" in data
        assert isinstance(data["comments"], list)

    def test_post_has_required_fields(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        post = data["post"]
        for key in ("title", "author", "upvotes", "selftext", "num_comments"):
            assert key in post


class TestJsonPostContent:
    """Post field values."""

    def test_post_title_author_upvotes_selftext(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        assert data["post"]["title"] == "Sample post title"
        assert data["post"]["author"] == "test_user"
        assert data["post"]["upvotes"] == 42
        assert data["post"]["selftext"] == "This is the post body."
        assert data["post"]["num_comments"] == 2


class TestJsonCommentsContent:
    """Nested comment structure and values."""

    def test_comments_list_length(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        assert len(data["comments"]) == 2

    def test_comment_has_author_score_body_replies(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        c = data["comments"][0]
        assert c["body"] == "First top-level comment."
        assert c["author"] == "commenter_one"
        assert c["score"] == 10
        assert "replies" in c
        assert isinstance(c["replies"], list)

    def test_nested_reply_content(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        reply = data["comments"][0]["replies"][0]
        assert reply["body"] == "A reply to the first comment."
        assert reply["author"] == "commenter_two"
        assert reply["score"] == 2
        assert reply["replies"] == []

    def test_deleted_author_in_json(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        deleted_comment = data["comments"][1]
        assert deleted_comment["author"] == "[deleted]"
        assert deleted_comment["body"] == "Deleted user comment."
        assert deleted_comment["score"] == -1


class TestJsonCommentDepth:
    """max_comment_depth for JSON."""

    def test_respects_max_comment_depth(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_json.max_comment_depth = 1
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        assert len(data["comments"]) == 2
        assert len(data["comments"][0]["replies"]) == 0

    def test_depth_zero_empty_comments(
        self, r2t_json: Reddit2Text, fake_submission: Any
    ) -> None:
        r2t_json.max_comment_depth = 0
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        assert data["comments"] == []
        assert data["post"]["title"] == "Sample post title"


class TestJsonEdgeCases:
    """Empty post body, no comments."""

    def test_minimal_post_no_comments(
        self, r2t_json: Reddit2Text, minimal_fake_submission: Any
    ) -> None:
        with patch.object(r2t_json, "_praw_reddit") as mock_reddit:
            mock_reddit.submission.return_value = minimal_fake_submission
            out = r2t_json.textualize_post(
                "https://reddit.com/r/fake/comments/abc123/"
            )
        data = json.loads(out)
        assert data["post"]["title"] == "Title only"
        assert data["post"]["selftext"] == ""
        assert data["post"]["num_comments"] == 0
        assert data["comments"] == []
