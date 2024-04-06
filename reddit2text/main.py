import praw
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
			author = comment.author.name if comment.author else "deleted"
			score = comment.score
			upvotes_or_downvotes = 'upvotes' if score >= 0 else 'downvotes'
			comment_body = comment.body.replace('\n', '\\n')  # Replace newlines to avoid breaking the tree structure

			comments_str += f"{prefix}{author} ({score} {upvotes_or_downvotes}): {comment_body}\n"

			# Recursively process the replies to each comment
			comments_str += self._process_comments(comment.replies, depth + 1)

		return comments_str

	def _process_original_post(self, post: praw.models.Submission) -> None:
		# Fetch the title, author, upvotes, and post text
		# OP's info
		title = post.title
		author = post.author.name if post.author else "deleted"
		upvotes = post.score
		selftext = post.selftext.replace('\n', ' ')  # Replace newlines to avoid breaking the structure

		# Ensure all comments are fetched
		post.comments.replace_more(limit=None)

		# Start building the final output string
		original_post_output = f"title: {title}\nauthor/upvotes: {author}/{upvotes}\npost text: {selftext}\n\n"

		return original_post_output

	def textualize_post(self, url: str) -> str:
		# Extract the post ID from the URL
		post_id = url.split('/')[-3]
		post = self._praw_reddit.submission(id=post_id)

		# Convert the original post and all the comments to text individually
		text_post = self._process_original_post(post)
		text_comments = self._process_comments(post.comments)

		# Combine the original post and comments into a single string
		final_output = text_post + text_comments

		# Handle the output based on the user's preference
		# self._handle_output(final_output)

		return final_output
