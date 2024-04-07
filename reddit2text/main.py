import praw
import re
from typing import Optional

class Reddit2Text:
	def __init__(
		self,
		client_id: str,
		client_secret: str,
		user_agent: str,
		*,
		max_comment_depth: Optional[int] = None,
		comment_delim: str = "|",
		save_output_to: Optional[str] = None
	) -> None:
		self.client_id = client_id
		self.client_secret = client_secret
		self.user_agent = user_agent
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

	def _process_comments(self, comments: praw.models.comment_forest.CommentForest, depth: int = 1) -> str:
		comments_str = ""
		for comment in comments:

			# Skip any 'MoreComments' objects
			if isinstance(comment, praw.models.MoreComments):
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
			comments_str += self._process_comments(comment.replies, depth + 1)

		return comments_str

	def _process_original_post(self, post: praw.models.Submission) -> None:
		# Fetch the title, author, upvotes, and post text
		# OP's info
		self.post_data = {
			'title': post.title,
			'author': post.author.name if post.author else "deleted",
			'upvotes': post.score,
			'selftext': re.sub(r'\n+', ' ', post.selftext),  # Replace newlines to avoid breaking the structure
			'num_comments': post.num_comments
		}

		# Ensure all comments are fetched
		if self.max_comment_depth != 0:
			post.comments.replace_more(limit=None)

		# Start building the final output string
		original_post_output = f"Title: {self.post_data['title']}\nAuthor: {self.post_data['author']}\nUpvotes: {self.post_data['upvotes']}\n"
		if self.post_data['selftext']:
			original_post_output += f"Body text: {self.post_data['selftext']}\n"

		return original_post_output

	def textualize_post(self, url: str) -> str:
		# PRAW auto-handles extracting the post ID from the URL
		# https://praw.readthedocs.io/en/stable/code_overview/models/submission.html
		post = self._praw_reddit.submission(url=url)
		self.post = post

		# Convert the original post and all the comments to text individually
		text_post = self._process_original_post(post)
		# A max_comment_depth of 0 means only the original post will be returned
		text_comments = ""
		if self.max_comment_depth != 0:
			text_comments = self._process_comments(post.comments)

		# Combine the original post and comments into a single string
		final_output = text_post + f'\n{self.post_data["num_comments"]} Comments:\n--------\n' + text_comments

		# Handle the output based on the user's preference
		# self._handle_output(final_output)

		return final_output
