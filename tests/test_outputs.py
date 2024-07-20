# pytest test file to verify the final output of the program

import pytest
import os
import re
from reddit2text.main import Reddit2Text

class TestFinalOutput():
	def test_output_txt(self):
		r2t = Reddit2Text(
			client_id=os.getenv('REDDIT_CLIENT_ID'),
			client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
			user_agent=os.getenv('REDDIT_USER_AGENT'),
			format='txt',
			save_output_to='tests/test_output.txt'
		)
		r2t.get_thread('https://www.reddit.com/r/learnpython/comments/ov9g2u/what_are_some_good_practices_to_follow_while/')
		with open('tests/test_output.txt') as f:
			output = f.read()
		assert re.match(r'^\*\*Title:\*\* What are some good practices to follow while writing a Python script\?\n\n\*\*Author:\*\* u\/[a-zA-Z0-9_]+\n\n\*\*Score:\*\* \d+\n\n\*\*Upvote Ratio:\*\* \d+\.\d{2}\n\n\*\*Awards:\*\* \d+\n\n\*\*Text:\*\* \n\nI am a beginner in Python and I have been writing scripts for a while now. I want to know what are some good practices that I should follow while writing a Python script. I have been following PEP8 and using type hints in my code. What else should I do to make my code better\?\n\n\*\*Comments:\*\*
