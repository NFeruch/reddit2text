import csv
import io
import json
import os
import re
from typing import TYPE_CHECKING, Any, List, Literal, Optional, Union

import praw
from dotenv import load_dotenv

from reddit2text.models import CommentDict, PostData, ThreadJson

_NEWLINES_RE = re.compile(r"\n+")

if TYPE_CHECKING:
    from praw.models.comment_forest import CommentForest

load_dotenv()


class Reddit2Text:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        *,
        format: Optional[Literal["txt", "json", "csv", "csv_relational"]] = "txt",
        max_comment_depth: Optional[int] = None,
        comment_delim: Optional[str] = "|",
        save_output_to: Optional[str] = None,
    ) -> None:
        """
        Parameters
        ----------
        client_id : str
                Generated with your Reddit API app
        client_secret : str
                Generated with your Reddit API app
        user_agent : str
                Tells the Reddit API who you are. Form:
                `<app type>:<app name>:<version> (by <your username>)`
        format : Literal['txt', 'json', 'csv', 'csv_relational'], optional
                Display format for the thread. Use 'csv_relational' for
                two CSVs (posts + comments) that can be joined like a DB.
                By default 'txt'
        max_comment_depth : int, optional
                Maximum depth of comments to output, including the top-most
                comment. 0 to exclude all; None or -1 to include all.
        comment_delim : str, optional
                String used to indent comments by nesting level, by default "|"
        save_output_to : str, optional
                Path to save the output, by default None
        """
        # Optionally fetch the credentials from the environment variables
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent or os.getenv("REDDIT_USER_AGENT")

        if not all((self.client_id, self.client_secret, self.user_agent)):
            raise ValueError(
                "Please provide client_id, client_secret, and user_agent"
            )

        self.format = format
        self.max_comment_depth = max_comment_depth
        self.comment_delim = comment_delim
        self.save_output_to = save_output_to

        self._praw_reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
        )

    def _handle_output(self, output: str) -> None:
        if self.save_output_to:
            with open(self.save_output_to, "w") as f:
                f.write(output)

    def _collect_comments(
        self,
        comments: "CommentForest",
        depth: int = 1,
    ) -> List[dict[str, Any]]:
        out: List[dict[str, Any]] = []
        if self.max_comment_depth == 0:
            return out
        max_depth = self.max_comment_depth
        stack: List[tuple[Any, int]] = [
            (c, depth)
            for c in reversed(list(comments))
            if not isinstance(c, praw.models.MoreComments)
        ]
        while stack:
            comment, d = stack.pop()
            if max_depth is not None and max_depth != -1 and d > max_depth:
                continue
            author = comment.author.name if comment.author else "[deleted]"
            body = _NEWLINES_RE.sub(" ", comment.body)
            out.append(
                {"depth": d, "author": author, "score": comment.score, "body": body}
            )
            if max_depth is None or max_depth == -1 or d + 1 <= max_depth:
                for reply in reversed(list(comment.replies)):
                    if not isinstance(reply, praw.models.MoreComments):
                        stack.append((reply, d + 1))
        return out

    def _collect_comments_relational(
        self,
        comments: "CommentForest",
        post_id: str,
        depth: int = 1,
    ) -> List[dict[str, Any]]:
        """Collect comments with comment_id and parent_id for relational CSV."""
        out: List[dict[str, Any]] = []
        if self.max_comment_depth == 0:
            return out
        max_depth = self.max_comment_depth
        stack: List[tuple[Any, int]] = [
            (c, depth)
            for c in reversed(list(comments))
            if not isinstance(c, praw.models.MoreComments)
        ]
        while stack:
            comment, d = stack.pop()
            if max_depth is not None and max_depth != -1 and d > max_depth:
                continue
            parent = comment.parent()
            parent_id = parent.id if hasattr(parent, "id") else post_id
            author = comment.author.name if comment.author else "[deleted]"
            body = _NEWLINES_RE.sub(" ", comment.body)
            out.append(
                {
                    "comment_id": comment.id,
                    "post_id": post_id,
                    "parent_id": parent_id,
                    "depth": d,
                    "author": author,
                    "score": comment.score,
                    "body": body,
                }
            )
            if max_depth is None or max_depth == -1 or d + 1 <= max_depth:
                for reply in reversed(list(comment.replies)):
                    if not isinstance(reply, praw.models.MoreComments):
                        stack.append((reply, d + 1))
        return out

    def _collect_comments_nested(
        self,
        comments: "CommentForest",
        depth: int = 1,
    ) -> List[CommentDict]:
        out: List[CommentDict] = []
        if self.max_comment_depth == 0:
            return out
        max_depth = self.max_comment_depth
        # Stack: (comment, depth, list to append this comment's dict to)
        stack: List[tuple[Any, int, List[CommentDict]]] = [
            (c, depth, out)
            for c in reversed(list(comments))
            if not isinstance(c, praw.models.MoreComments)
        ]
        while stack:
            comment, d, parent_list = stack.pop()
            if max_depth is not None and max_depth != -1 and d > max_depth:
                continue
            author = comment.author.name if comment.author else "[deleted]"
            body = _NEWLINES_RE.sub(" ", comment.body)
            node: CommentDict = {
                "author": author,
                "score": comment.score,
                "body": body,
                "replies": [],
            }
            parent_list.append(node)
            if max_depth is None or max_depth == -1 or d + 1 <= max_depth:
                for reply in reversed(list(comment.replies)):
                    if not isinstance(reply, praw.models.MoreComments):
                        stack.append((reply, d + 1, node["replies"]))
        return out

    def _process_comments(
        self,
        comments: "CommentForest",
        depth: int = 1,
    ) -> str:
        if self.max_comment_depth == 0:
            return ""
        max_depth = self.max_comment_depth
        parts: List[str] = []
        stack: List[tuple[Any, int]] = [
            (c, depth)
            for c in reversed(list(comments))
            if not isinstance(c, praw.models.MoreComments)
        ]
        while stack:
            comment, d = stack.pop()
            if max_depth is not None and max_depth != -1 and d > max_depth:
                continue
            prefix = f"{self.comment_delim} " * d
            author = comment.author.name if comment.author else "[deleted]"
            score = comment.score
            upvotes_or_downvotes = "upvotes" if score >= 0 else "downvotes"
            comment_body = _NEWLINES_RE.sub(" ", comment.body)
            parts.append(
                f"{prefix}{author} ({score} {upvotes_or_downvotes}): "
                f"{comment_body}\n"
            )
            if max_depth is None or max_depth == -1 or d + 1 <= max_depth:
                for reply in reversed(list(comment.replies)):
                    if not isinstance(reply, praw.models.MoreComments):
                        stack.append((reply, d + 1))
        return "".join(parts)

    def _format_json(
        self,
        post_data: PostData,
        comments_list: List[CommentDict],
    ) -> str:
        obj: ThreadJson = {"post": post_data, "comments": comments_list}
        return json.dumps(obj, indent=2)

    def _format_csv(
        self,
        post_data: dict[str, Any],
        comments_list: List[dict[str, Any]],
    ) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["depth", "author", "score", "body"])
        # Post as first row with depth 0
        w.writerow(
            [
                0,
                post_data["author"],
                post_data["upvotes"],
                (
                    post_data["title"]
                    + (
                        " " + post_data["selftext"]
                        if post_data["selftext"]
                        else ""
                    )
                ).strip(),
            ]
        )
        for c in comments_list:
            w.writerow([c["depth"], c["author"], c["score"], c["body"]])
        return buf.getvalue()

    def _format_csv_relational(
        self,
        post_id: str,
        post_data: dict[str, Any],
        comments_list: List[dict[str, Any]],
    ) -> tuple[str, str]:
        """Return (posts_csv, comments_csv) for relational output."""
        posts_buf = io.StringIO()
        posts_w = csv.writer(posts_buf)
        posts_w.writerow(
            ["post_id", "title", "author", "upvotes", "selftext", "num_comments"]
        )
        posts_w.writerow(
            [
                post_id,
                post_data["title"],
                post_data["author"],
                post_data["upvotes"],
                post_data["selftext"],
                post_data["num_comments"],
            ]
        )
        comments_buf = io.StringIO()
        comments_w = csv.writer(comments_buf)
        comments_w.writerow(
            [
                "comment_id",
                "post_id",
                "parent_id",
                "depth",
                "author",
                "score",
                "body",
            ]
        )
        for c in comments_list:
            comments_w.writerow(
                [
                    c["comment_id"],
                    c["post_id"],
                    c["parent_id"],
                    c["depth"],
                    c["author"],
                    c["score"],
                    c["body"],
                ]
            )
        return posts_buf.getvalue(), comments_buf.getvalue()

    def _process_original_post(self, thread: praw.models.Submission) -> str:
        # Fetch the title, author, upvotes, and post text
        # OP's info
        self.post_data: PostData = {
            "title": thread.title,
            "author": thread.author.name if thread.author else "deleted",
            "upvotes": thread.score,
            "selftext": _NEWLINES_RE.sub(" ", thread.selftext),  # Replace newlines to avoid breaking the structure
            "num_comments": thread.num_comments,
        }

        # Ensure all comments are fetched
        if self.max_comment_depth != 0:
            thread.comments.replace_more(limit=None)

        # Start building the final output string
        pd = self.post_data
        original_post_output = (
            f"Title: {pd['title']}\nAuthor: {pd['author']}\n"
            f"Upvotes: {pd['upvotes']}\n"
        )
        if pd["selftext"]:
            original_post_output += f"Body text: {pd['selftext']}\n"

        return original_post_output

    def textualize_post(
        self, urls: Union[str, List[str]]
    ) -> Union[str, List[str]]:
        if isinstance(urls, str):
            urls = [urls]

        final_outputs = []

        for url in urls:
            # PRAW auto-handles extracting the post ID from the URL
            reddit = self._praw_reddit
            thread = reddit.submission(url=url)

            # Convert the original post and comments
            self._process_original_post(thread)
            pd = self.post_data

            if self.format == "json":
                comments_nested = self._collect_comments_nested(
                    thread.comments
                )
                final_output = self._format_json(pd, comments_nested)
            elif self.format == "csv":
                comments_list = self._collect_comments(thread.comments)
                final_output = self._format_csv(
                    dict[str, Any](pd), comments_list
                )
            elif self.format == "csv_relational":
                post_id = thread.id
                comments_list = self._collect_comments_relational(
                    thread.comments, post_id
                )
                posts_csv, comments_csv = self._format_csv_relational(
                    post_id, dict[str, Any](pd), comments_list
                )
                if self.save_output_to:
                    base = self.save_output_to.rsplit(".", 1)[0] if "." in self.save_output_to else self.save_output_to
                    with open(f"{base}_posts.csv", "w") as f:
                        f.write(posts_csv)
                    with open(f"{base}_comments.csv", "w") as f:
                        f.write(comments_csv)
                final_output = posts_csv
            else:
                text_post = (
                    f"Title: {pd['title']}\nAuthor: {pd['author']}\n"
                    f"Upvotes: {pd['upvotes']}\n"
                )
                if pd["selftext"]:
                    text_post += f"Body text: {pd['selftext']}\n"
                text_comments = self._process_comments(thread.comments)
                comment_header = (
                    f"\n{pd['num_comments']} Comments:\n--------\n"
                    if self.max_comment_depth != 0
                    else ""
                )
                final_output = text_post + comment_header + text_comments

            if self.save_output_to and self.format != "csv_relational":
                self._handle_output(final_output)
            final_outputs.append(final_output)

        if len(final_outputs) == 1:
            return final_outputs[0]
        return final_outputs
