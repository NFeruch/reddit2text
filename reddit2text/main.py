import praw
import re
from typing import Optional, Literal
import os
from dotenv import load_dotenv

load_dotenv()

class Reddit2Text:
    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        user_agent: str = None,
        *,
        format: Optional[Literal['txt', 'json', 'csv']] = 'txt',
        max_comment_depth: Optional[int] = None,
        comment_delim: Optional[str] = "|",
        save_output_to: Optional[str] = None
    ) -> None:
        """
        Parameters
        ----------
        client_id : str
            Generated with your Reddit API app
        client_secret : str
            Generated with your Reddit API app
        user_agent : str
            Tells the Reddit API who you are, of the form, `<app type>:<app name>:<version> (by <your username>)`
        format : Literal['txt', 'json', 'csv'], optional
            How you want the Reddit thread to be displayed, by default 'txt'
        max_comment_depth : int, optional
            Maximum depth of comments to output, including the top-most comment. Choose 0 to exclude all comments, by default None or -1 to include all
        comment_delim : str, optional
            String/character used to indent comments according to their nesting level, by default "|"
        save_output_to : str, optional
            The location in which you want to save the output, by default None
        """
        # Optionally fetch the credentials from the environment variables
        self.client_id = client_id or os.getenv('REDDIT_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('REDDIT_CLIENT_SECRET')
        self.user_agent = user_agent or os.getenv('REDDIT_USER_AGENT')

        if not all((self.client_id, self.client_secret, self.user_agent)):
            raise ValueError("Please provide client_id, client_secret, and user_agent")

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
            with open(self.save_output_to, 'w') as f:
                f.write(output)
    

    def _process_comments(self, comments: praw.models.comment_forest.CommentForest, min_upvotes, max_upvotes, min_length, max_length, min_time, max_time, score_sort_order, length_sort_order, time_sort_order, filter_text, filter_author, submitter, depth: int = 1) -> str:
        comments_str = ""

        # A max_comment_depth of 0 means only the original post will be returned
        if self.max_comment_depth == 0:
            return comments_str

        sorted_comments = comments

        #sorting features
        if score_sort_order is not None:
            sorted_comments = sorted(sorted_comments, key=lambda x: x.score, reverse=(score_sort_order == 'descending'))
    
        if length_sort_order is not None:
            sorted_comments = sorted(sorted_comments, key=lambda x: len(x.body), reverse=(length_sort_order == 'descending'))

        if time_sort_order is not None:
            sorted_comments = sorted(sorted_comments, key=lambda x: x.created_utc, reverse=(time_sort_order == 'descending'))

        text_pattern = re.compile(filter_text, re.IGNORECASE) if filter_text else None
        author_pattern = re.compile(filter_author, re.IGNORECASE) if filter_author else None

        for comment in sorted_comments:

            # Skip any 'MoreComments' objects
            if isinstance(comment, praw.models.MoreComments):
                continue

            # Filtering features
            # If submitter is not None and (comment.is_submitter != submitter): #Checks to be done from 2nd level
            #     continue

            if min_upvotes is not None and comment.score < min_upvotes:
                continue

            if max_upvotes is not None and comment.score > max_upvotes:
                continue

            if min_length is not None and len(comment.body) < min_length:
                continue
    
            if max_length is not None and len(comment.body) > max_length:
                continue

            if min_time is not None and comment.created_utc < min_time:
                continue

            if max_time is not None and comment.created_utc > max_time:
                continue

            if text_pattern is not None and (not text_pattern.search(comment.body)):
                continue
    
            if author_pattern is not None:
                if comment.author:
                    if not author_pattern.search(comment.author.name):
                        continue
                else:
                    continue

            # Media content check pattern
            media_patterns = [
                r'(https?://)?(www\.)?(reddit\.com/)?(r/[a-zA-Z0-9_]+/)?(comments/[a-zA-Z0-9]+/)?(gallery|media|video|gif|jpg|jpeg|png|gifv)',
                # Add more patterns as needed to capture various forms of media content
            ]

            # Check if the comment has media content
            flag = False
            for pattern in media_patterns:
                if re.search(pattern, comment.body, re.IGNORECASE):
                    flag=True

            # Ignore if comment contains media content
            if flag:
                continue


            # Stop processing comments if depth exceeds max_comment_depth
            if self.max_comment_depth not in (None, -1) and depth > self.max_comment_depth:
                break

            prefix = f"{self.comment_delim} " * depth

            # Safe-guard for deleted comments where the author would be None
            author = comment.author.name if comment.author else "[deleted]"
            score = comment.score
            upvotes_or_downvotes = 'upvotes' if score >= 0 else 'downvotes'
            comment_body = re.sub(r'\n+', ' ', comment.body)  # Replace newlines to avoid breaking the tree structure

            comments_str += f"{prefix}{author} ({score} {upvotes_or_downvotes}): {comment_body}\n"
            
            # Recursively process the replies to each comment
            comments_str += self._process_comments(comment.replies, min_upvotes=min_upvotes, max_upvotes=max_upvotes, min_length=min_length, max_length=max_length, min_time=min_time, max_time=max_time, score_sort_order=score_sort_order, length_sort_order=length_sort_order, time_sort_order=time_sort_order, filter_text=filter_text, filter_author=filter_author, submitter=submitter, depth=depth + 1)

        return comments_str

    def _process_original_post(self, thread: praw.models.Submission) -> str:
        # Fetch the title, author, upvotes, and post text
        # OP's info
        self.post_data = {
            'title': thread.title,
            'author': thread.author.name if thread.author else "deleted",
            'upvotes': thread.score,
            'selftext': re.sub(r'\n+', ' ', thread.selftext),  # Replace newlines to avoid breaking the structure
            'num_comments': thread.num_comments
        }

        # Ensure all comments are fetched
        if self.max_comment_depth != 0:
            thread.comments.replace_more(limit=None)

        # Start building the final output string
        original_post_output = f"Title: {self.post_data['title']}\nAuthor: {self.post_data['author']}\nUpvotes: {self.post_data['upvotes']}\n"
        if self.post_data['selftext']:
            original_post_output += f"Body text: {self.post_data['selftext']}\n"

        return original_post_output

    def textualize_post(self, url, min_upvotes, max_upvotes, min_length, max_length, min_time, max_time, score_sort_order, length_sort_order, time_sort_order, filter_text, filter_author, submitter) -> str:
        # PRAW auto-handles extracting the post ID from the URL
        # https://praw.readthedocs.io/en/stable/code_overview/models/submission.html
        # print('Getting thread...')
        thread = self._praw_reddit.submission(url=url)

        # Convert the original post and all the comments to text individually
        # print('Processing thread...')
        text_post = self._process_original_post(thread)

        # Ensure all comments are fetched
        # print('Processing comments...')
        text_comments = self._process_comments(thread.comments, min_upvotes=min_upvotes, max_upvotes=max_upvotes, min_length=min_length, max_length=max_length, min_time=min_time, max_time=max_time, score_sort_order=score_sort_order, length_sort_order=length_sort_order, time_sort_order=time_sort_order, filter_text=filter_text, filter_author=filter_author, submitter=submitter)

        comment_header = f'\n{self.post_data["num_comments"]} Comments:\n--------\n' if self.max_comment_depth != 0 else ''

        # Combine the original post and comments into a single string
        final_output = text_post + comment_header + text_comments

        # Handle the output based on the user's preference
        # self._handle_output(final_output)

        return final_output
