import praw
import re
import os
import json
from datetime import datetime
import pandas as pd
from typing import Optional, Literal, Union
from dotenv import load_dotenv

load_dotenv()

class Reddit2Text:
	valid_formats = ('txt', 'json', 'csv')

	def __init__(
		self,
		client_id: str = None,
		client_secret: str = None,
		user_agent: str = None,
		*,
		format: Optional[Literal['txt', 'json', 'csv']] = 'txt',
		save_output_to: Optional[str] = None,
		max_comment_depth: Optional[int] = None,
		text_comment_delim: Optional[str] = "|",
		json_indent: Optional[int] = 4,
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
		if format not in self.valid_formats:
			raise ValueError(f"Invalid format. Choose from {self.valid_formats}")

		if format == 'text':
			format = 'txt'
		self.format = format

		self.max_comment_depth = max_comment_depth
		self.comment_delim = text_comment_delim
		self.save_output_to = save_output_to
		self.json_indent = json_indent

		self._praw_reddit = praw.Reddit(
			client_id=self.client_id,
			client_secret=self.client_secret,
			user_agent=self.user_agent,
		)

	def _handle_output(self, output):
		# Delegate to the appropriate method based on the format
		if self.format == 'csv':
			self._handle_csv(output)
		elif self.format == 'json':
			self._handle_json(output)
		elif self.format == 'txt':
			self._handle_txt(output)

	def _construct_file_paths(self, extension):
		directory, filename_with_ext = os.path.split(self.save_output_to)
		# Check if a directory was provided or if it's just a filename
		if not directory:
			directory = "."  # Current directory
		if self.save_output_to.endswith(extension):
			filename = filename_with_ext[:-len(extension)]  # Remove extension
		else:
			# If no extension in save_output_to, use it as filename or default to datetime
			filename = filename_with_ext if filename_with_ext else datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		os.makedirs(directory, exist_ok=True)
		return directory, filename

	def _handle_csv(self, output):
		directory, filename = self._construct_file_paths('.csv')
		post_file_path = os.path.join(directory, f"{filename}_posts.csv")
		comments_file_path = os.path.join(directory, f"{filename}_comments.csv")
		posts_df, comments_df = output
		posts_df.to_csv(post_file_path, index=False)
		comments_df.to_csv(comments_file_path, index=False)

	def _handle_json(self, output):
		directory, filename = self._construct_file_paths('.json')
		file_path = os.path.join(directory, f"{filename}.json")
		with open(file_path, 'w', encoding='utf-8') as f:
			json.dump(json.loads(output), f, indent=self.json_indent)

	def _handle_txt(self, output):
		directory, filename = self._construct_file_paths('.txt')
		file_path = os.path.join(directory, f"{filename}.txt")
		with open(file_path, 'w') as f:
			f.write(output)

	def _process_comments(self, comments: praw.models.comment_forest.CommentForest, depth: int = 1) -> str:
		comments_json = []

		# A max_comment_depth of 0 means only the post will be returned
		if self.max_comment_depth == 0:
			return comments_json

		for comment in comments:
			# Stop processing comments if depth exceeds max_comment_depth
			if self.max_comment_depth not in (None, -1) and depth > self.max_comment_depth:
				break


			self.comment_json = {
				'id': comment.id,
				'permalink': f"https://reddit.com{comment.permalink}",
				'created_utc': comment.created_utc,
				'post_id': comment.submission.id,
				'is_top_level_comment': 't3_' in comment.parent_id,
				'parent_comment_id': comment.parent_id.replace('t1_', '') if 't1_' in comment.parent_id else None,
				'depth': depth,
				'author': comment.author.name if comment.author else "[deleted]",
				'score': comment.score,
				'comment_text': re.sub(r'\n+', ' ', comment.body)  # Replace newlines to avoid breaking the tree structure
			}

			comments_json.append(self.comment_json)
			# Recursively process the replies to each comment
			comments_json += self._process_comments(comment.replies, depth + 1)

		return comments_json

	def _process_post(self, thread: praw.models.Submission) -> str:
		# Fetch the title, author, upvotes, and post text
		# OP's info
		self.post_json = {
			'id': thread.id,
			'title': thread.title,
			'url': thread.url,
			'created_utc': thread.created_utc,
			'subreddit': f"/r/{thread.subreddit.display_name}",
			'author': thread.author.name if thread.author else "deleted",
			'upvotes': thread.score,
			'body_text': re.sub(r'\n+', ' ', thread.selftext),  # Replace newlines to avoid breaking the structure
			'num_comments': thread.num_comments
		}

		# Ensure all comments are fetched
		if self.max_comment_depth != 0:
			thread.comments.replace_more(limit=None)

		# if self.format == 'txt':
		# 	# Start building the final output string
		# 	post_text_output = f"Title: {self.post_json['title']}\nAuthor: {self.post_json['author']}\nUpvotes: {self.post_json['upvotes']}\n"
		# 	if self.post_json['body_text']:
		# 		post_text_output += f"Body text: {self.post_json['body_text']}\n"
		# 	return post_text_output

		return self.post_json

	def _conform_data_to_format(self, post_data: dict, comments_data: list) -> str:
		if self.format == 'txt':
			# Start building the final output string
			post_text_output = f"""\
			Subreddit: {post_data['subreddit']}
			Title: {post_data['title']}
			Author: {post_data['author']}
			Created At: {pd.to_datetime(post_data['created_utc'], unit='s')}
			Upvotes: {post_data['upvotes']}
			\
			""".replace("\t", "")

			if post_data['body_text']:
				post_text_output += f"Body text: {post_data['body_text']}\n"

			if post_data['num_comments'] == 0 or self.max_comment_depth == 0:
				return post_text_output

			comments_header = f"{post_data['num_comments']} Comments:"
			comments_str = f"\n{comments_header}\n{'-' * len(comments_header)}\n"
			for comment in comments_data:
				txt_prefix = f"{self.comment_delim} " * comment['depth']
				upvotes_or_downvotes = 'upvotes' if comment['score'] >= 0 else 'downvotes'
				created_at = pd.to_datetime(comment['created_utc'], unit='s')
				comments_str += f"{txt_prefix}{comment['author']} ({comment['score']} {upvotes_or_downvotes}, {created_at}): {comment['comment_text']}\n"

			return post_text_output + comments_str

		elif self.format == 'json':
			return json.dumps({
				'post': post_data,
				'comments': comments_data
			}, indent=self.json_indent)

		elif self.format == 'csv':
			post_csv = pd.DataFrame([post_data])
			post_csv['created_utc'] = pd.to_datetime(post_csv['created_utc'], unit='s')
			comments_csv = pd.DataFrame(comments_data)
			comments_csv['created_utc'] = pd.to_datetime(comments_csv['created_utc'], unit='s')
			return [post_csv, comments_csv]

	def textualize_post(self, url: str) -> str:
		# PRAW auto-handles extracting the post ID from the URL
		# https://praw.readthedocs.io/en/stable/code_overview/models/submission.html
		thread = self._praw_reddit.submission(url=url)

		post_data = self._process_post(thread)
		comments_data = self._process_comments(thread.comments)

		formatted_output = self._conform_data_to_format(post_data, comments_data)

		if self.save_output_to:
			self._handle_output(formatted_output)

		return formatted_output
