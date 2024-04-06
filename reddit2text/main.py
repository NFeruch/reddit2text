import praw

class Client:
	def __init__(
		self,
		client_id: str,
		client_secret: str,
		user_agent: str,
	) -> None:
		self.client_id = client_id
		self.client_secret = client_secret
		self.user_agent = user_agent

		self.praw_reddit = praw.Reddit(
			client_id=self.client_id,
			client_secret=self.client_secret,
			user_agent=self.user_agent,
		)

	def _process_comments(self, comments: praw.models.comment_forest, depth=0) -> str:
		comments_str = ""
		for comment in comments:
			if isinstance(comment, praw.models.MoreComments):
				continue  # Skip any 'MoreComments' objects

			prefix = "| " * (depth + 1)

			# Safe-guard for deleted comments where the author would be None
			author = comment.author.name if comment.author else "deleted"
			upvotes = comment.score
			comment_body = comment.body.replace('\n', '\\n')  # Replace newlines to avoid breaking the tree structure

			comments_str += f"{prefix}{author} ({upvotes} upvotes): {comment_body}\n"

			# Recursively process the replies to each comment
			comments_str += self._process_comments(comment.replies, depth + 1)

		return comments_str

	def textualize_post(self, url: str) -> str:
		# Extract the post ID from the URL
		post_id = url.split('/')[-3]

		# Fetch the post by ID
		post = self.praw_reddit.submission(id=post_id)

		# Fetch the title, author, upvotes, and post text
		title = post.title
		author = post.author.name if post.author else "deleted"
		upvotes = post.score
		selftext = post.selftext.replace('\n', ' ')  # Replace newlines to avoid breaking the structure

		# Ensure all comments are fetched
		post.comments.replace_more(limit=None)

		# Start building the final output string
		final_output = f"title: {title}\nauthor/upvotes: {author}/{upvotes}\npost text: {selftext}\n\n"

		# Add the processed comments and replies to the final output
		final_output += self._process_comments(post.comments)

		return final_output
