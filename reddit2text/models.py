"""Type definitions for Reddit thread and comment structures."""

from __future__ import annotations

from typing import List, TypedDict


class PostData(TypedDict):
    """Top-level post (submission) fields."""

    title: str
    author: str
    upvotes: int
    selftext: str
    num_comments: int


class CommentDict(TypedDict):
    """
    Recursive comment: each comment has a list of replies with the same shape.
    No 'depth' field; structure is implied by nesting.
    """

    author: str
    score: int
    body: str
    replies: List["CommentDict"]


class ThreadJson(TypedDict):
    """Full JSON output for a single thread (post + nested comments)."""

    post: PostData
    comments: List[CommentDict]
