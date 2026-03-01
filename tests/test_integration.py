"""Integration tests against the real Reddit API using archived posts.

Archived posts are read-only, so content is stable. All tests run against
two fixed URLs (small + large thread) for extra coverage. Skip when
credentials are not set (e.g. no .env or REDDIT_CLIENT_ID).
"""

import io
import json
import os
from pathlib import Path

import pytest

from reddit2text.main import Reddit2Text

# (url, topic keywords: any of these should appear in post content/title)
ARCHIVED_POSTS = [
    (
        "https://www.reddit.com/r/AmItheAsshole/comments/dao6ps/"
        "aitah_for_calling_my_pregnant_sister_a_bitch/",
        ("sister", "asshole", "aita"),
    ),
    (
        "https://www.reddit.com/r/AmItheAsshole/comments/btxcbh/"
        "aitah_for_being_upset_at_my_wife_for_not_telling/",
        ("wife", "asshole", "aita"),
    ),
]

ARCHIVED_POST_IDS = [f"post_{i}" for i in range(len(ARCHIVED_POSTS))]


def _has_credentials() -> bool:
    return bool(
        os.getenv("REDDIT_CLIENT_ID")
        and os.getenv("REDDIT_CLIENT_SECRET")
        and os.getenv("REDDIT_USER_AGENT")
    )


@pytest.fixture(scope="module")
def r2t_integration():
    """Reddit2Text with env credentials; skip if not configured."""
    if not _has_credentials():
        pytest.skip("Reddit API credentials not set (REDDIT_CLIENT_ID, etc.)")
    return Reddit2Text()


def _topic_ok(text: str, keywords: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(k in lower for k in keywords)


@pytest.mark.integration
@pytest.mark.parametrize("url,keywords", ARCHIVED_POSTS, ids=ARCHIVED_POST_IDS)
class TestArchivedPostTxt:
    def test_returns_non_empty_text(
        self, r2t_integration: Reddit2Text, url: str, keywords: tuple[str, ...]
    ) -> None:
        r2t_integration.format = "txt"
        out = r2t_integration.textualize_post(url)
        assert isinstance(out, str)
        assert len(out.strip()) > 0
        assert "Title:" in out
        assert "Author:" in out
        assert "Upvotes:" in out

    def test_contains_expected_topic(
        self, r2t_integration: Reddit2Text, url: str, keywords: tuple[str, ...]
    ) -> None:
        r2t_integration.format = "txt"
        out = r2t_integration.textualize_post(url)
        assert _topic_ok(out, keywords)


@pytest.mark.integration
@pytest.mark.parametrize("url,keywords", ARCHIVED_POSTS, ids=ARCHIVED_POST_IDS)
class TestArchivedPostJson:
    def test_returns_valid_json_with_post_and_comments(
        self, r2t_integration: Reddit2Text, url: str, keywords: tuple[str, ...]
    ) -> None:
        r2t_integration.format = "json"
        out = r2t_integration.textualize_post(url)
        data = json.loads(out)
        assert "post" in data
        assert "comments" in data
        assert "title" in data["post"]
        assert "author" in data["post"]
        assert isinstance(data["comments"], list)

    def test_post_has_expected_topic(
        self, r2t_integration: Reddit2Text, url: str, keywords: tuple[str, ...]
    ) -> None:
        r2t_integration.format = "json"
        out = r2t_integration.textualize_post(url)
        data = json.loads(out)
        title = data["post"]["title"].lower()
        assert _topic_ok(title, keywords)


@pytest.mark.integration
@pytest.mark.parametrize("url,keywords", ARCHIVED_POSTS, ids=ARCHIVED_POST_IDS)
class TestArchivedPostCsv:
    def test_returns_csv_with_header_and_rows(
        self, r2t_integration: Reddit2Text, url: str, keywords: tuple[str, ...]
    ) -> None:
        r2t_integration.format = "csv"
        out = r2t_integration.textualize_post(url)
        lines = out.strip().split("\n")
        assert len(lines) >= 2
        assert "depth,author,score,body" in lines[0] or lines[0].startswith(
            "depth"
        )


@pytest.mark.integration
@pytest.mark.parametrize("url,keywords", ARCHIVED_POSTS, ids=ARCHIVED_POST_IDS)
class TestArchivedPostCsvRelational:
    """Relational CSVs: posts + comments with IDs for DB-like joins."""

    def test_returns_posts_csv_and_writes_two_files(
        self,
        r2t_integration: Reddit2Text,
        url: str,
        keywords: tuple[str, ...],
        tmp_path_factory: pytest.TempPathFactory,
    ) -> None:
        import csv as csv_module

        r2t_integration.format = "csv_relational"
        r2t_integration.save_output_to = str(
            tmp_path_factory.mktemp("rel") / "thread.csv"
        )
        out = r2t_integration.textualize_post(url)
        # Return value is posts CSV
        rows = list(csv_module.reader(io.StringIO(out)))
        assert rows[0] == [
            "post_id",
            "title",
            "author",
            "upvotes",
            "selftext",
            "num_comments",
        ]
        assert len(rows) == 2
        assert rows[1][0]  # post_id present
        # Two files written
        base = r2t_integration.save_output_to.rsplit(".", 1)[0] if "." in r2t_integration.save_output_to else r2t_integration.save_output_to
        posts_path = f"{base}_posts.csv"
        comments_path = f"{base}_comments.csv"
        assert Path(posts_path).exists()
        assert Path(comments_path).exists()
        comments_rows = list(
            csv_module.reader(io.StringIO(Path(comments_path).read_text()))
        )
        assert comments_rows[0] == [
            "comment_id",
            "post_id",
            "parent_id",
            "depth",
            "author",
            "score",
            "body",
        ]
        assert len(comments_rows) >= 2
