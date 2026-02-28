import os
import re
from typing import TYPE_CHECKING, List, Literal, Optional, Union

import praw
from dotenv import load_dotenv

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
        format: Optional[Literal["txt", "json", "csv"]] = "txt",
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
        format : Literal['txt', 'json', 'csv'], optional
                Display format for the thread, by default 'txt'
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

    def _process_comments(
        self,
        comments: "CommentForest",
        depth: int = 1,
    ) -> str:
        comments_str = ""

        # max_comment_depth of 0 means only the original post is returned
        if self.max_comment_depth == 0:
            return comments_str

        for comment in comments:
            # Skip any 'MoreComments' objects
            if isinstance(comment, praw.models.MoreComments):
                continue

            # Stop processing comments if depth exceeds max_comment_depth
            max_depth = self.max_comment_depth
            if max_depth is not None and max_depth != -1 and depth > max_depth:
                break

            prefix = f"{self.comment_delim} " * depth

            # Safe-guard for deleted comments where the author would be None
            author = comment.author.name if comment.author else "[deleted]"
            score = comment.score
            upvotes_or_downvotes = "upvotes" if score >= 0 else "downvotes"
            comment_body = re.sub(
                r"\n+", " ", comment.body
            )  # Replace newlines to avoid breaking the tree structure

            comments_str += (
                f"{prefix}{author} ({score} {upvotes_or_downvotes}): "
                f"{comment_body}\n"
            )

            # Recursively process the replies to each comment
            comments_str += self._process_comments(comment.replies, depth + 1)

        return comments_str

    def _process_original_post(self, thread: praw.models.Submission) -> str:
        # Fetch the title, author, upvotes, and post text
        # OP's info
        self.post_data = {
            "title": thread.title,
            "author": thread.author.name if thread.author else "deleted",
            "upvotes": thread.score,
            "selftext": re.sub(
                r"\n+", " ", thread.selftext
            ),  # Replace newlines to avoid breaking the structure
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

            # Convert the original post and comments to text
            text_post = self._process_original_post(thread)

            # Ensure all comments are fetched
            text_comments = self._process_comments(thread.comments)

            comment_header = (
                f"\n{self.post_data['num_comments']} Comments:\n--------\n"
                if self.max_comment_depth != 0
                else ""
            )

            # Combine the original post and comments into a single string
            final_output = text_post + comment_header + text_comments

            final_outputs.append(final_output)

        if len(final_outputs) == 1:
            return final_outputs[0]
        return final_outputs
