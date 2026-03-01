"""Pytest fixtures and fake PRAW-like objects built from JSON fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from reddit2text.models import CommentDict, ThreadJson

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def _make_author(name: str) -> Any:
    """Object with .name used as comment.author / thread.author."""

    class Author:
        def __init__(self, n: str) -> None:
            self.name = n

    return Author(name) if name != "[deleted]" else None


class FakeComment:
    """Minimal comment-like object for the attributes main.py uses."""

    def __init__(
        self,
        *,
        comment_id: str,
        author: Any,
        body: str,
        score: int,
        replies: list["FakeComment"],
        parent: Any,
    ) -> None:
        self.id = comment_id
        self.author = author
        self.body = body
        self.score = score
        self.replies = replies
        self._parent = parent

    def parent(self) -> Any:
        return self._parent


class FakeSubmission:
    """Submission-like object; .comments has replace_more(limit=None) no-op."""

    def __init__(
        self,
        *,
        title: str,
        author: Any,
        score: int,
        selftext: str,
        num_comments: int,
        comments: list[FakeComment],
        submission_id: str = "post",
    ) -> None:
        self.id = submission_id
        self.title = title
        self.author = author
        self.score = score
        self.selftext = selftext
        self.num_comments = num_comments
        self._comments = comments

    @property
    def comments(self) -> "FakeCommentForest":
        return FakeCommentForest(self._comments)


def _comments_from_fixture(
    comments: list[CommentDict],
    parent: Any,
    prefix: str = "c",
) -> list[FakeComment]:
    out: list[FakeComment] = []
    for i, c in enumerate(comments):
        comment_id = f"{prefix}{i}"
        fake = FakeComment(
            comment_id=comment_id,
            author=_make_author(c["author"]),
            body=c["body"],
            score=c["score"],
            replies=[],
            parent=parent,
        )
        fake.replies = _comments_from_fixture(
            c.get("replies") or [], parent=fake, prefix=f"{comment_id}_"
        )
        out.append(fake)
    return out


class FakeCommentForest:
    """Iterable comment list with replace_more(limit=None) no-op."""

    def __init__(self, comments: list[FakeComment]) -> None:
        self._comments = comments

    def replace_more(self, limit: int | None = None) -> None:
        pass

    def __iter__(self) -> Any:
        return iter(self._comments)


def load_thread_fixture(name: str) -> ThreadJson:
    """Load a thread fixture by name (e.g. 'sample_thread')."""
    path = FIXTURES_DIR / f"{name}.json"
    with open(path) as f:
        data: ThreadJson = json.load(f)
    return data


def fake_submission_from_fixture(data: ThreadJson) -> FakeSubmission:
    """Build a FakeSubmission from fixture data (ThreadJson shape)."""
    post = data["post"]
    author_name = post["author"]
    post_stub = type("_PostStub", (), {"id": "post"})()
    return FakeSubmission(
        title=post["title"],
        author=_make_author(author_name) if author_name != "deleted" else None,
        score=post["upvotes"],
        selftext=post["selftext"],
        num_comments=post["num_comments"],
        comments=_comments_from_fixture(data["comments"], post_stub),
        submission_id="post",
    )


@pytest.fixture
def sample_thread_data() -> ThreadJson:
    """Loaded sample_thread.json."""
    return load_thread_fixture("sample_thread")


@pytest.fixture
def fake_submission(sample_thread_data: ThreadJson) -> FakeSubmission:
    """Fake PRAW submission built from sample_thread.json."""
    return fake_submission_from_fixture(sample_thread_data)


@pytest.fixture
def minimal_thread_data() -> ThreadJson:
    """Loaded minimal_thread.json (no selftext, no comments)."""
    return load_thread_fixture("minimal_thread")


@pytest.fixture
def minimal_fake_submission(minimal_thread_data: ThreadJson) -> FakeSubmission:
    """Fake PRAW submission built from minimal_thread.json."""
    return fake_submission_from_fixture(minimal_thread_data)
