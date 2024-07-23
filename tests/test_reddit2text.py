import pytest
from reddit2text import Reddit2Text
import pandas as pd
import pickle
import os

PICKLE_PATH = 'tests/reddit2text.pkl'

@pytest.fixture
def reddit2text():
	if os.path.exists(PICKLE_PATH):
		with open(PICKLE_PATH, 'rb') as f:
			reddit2text_instance = pickle.load(f)
	else:
		reddit2text_instance = Reddit2Text(
			client_id='OQNCb0uiwq1FTgN4qGpHqg',
			client_secret='eb-6Qdyapcrmq8wteFhIe6wPEhEjHQ',
			user_agent='script:my_app:v1.0 (by u/fragheytad113)'
		)
		with open(PICKLE_PATH, 'wb') as f:
			pickle.dump(reddit2text_instance, f)
	
	return reddit2text_instance

@pytest.fixture
def test_data():
	return pd.read_csv('tests/test_data.csv')

def normalize_text(text):
	return ' '.join(text.split()).strip()

def test_reddit2text(reddit2text: Reddit2Text, test_data: pd.DataFrame):
	url = "https://www.reddit.com/r/reddit2text_testing/comments/1dkot3x/this_is_a_test_reddit_post_with_a_title_and_body/"
	output = reddit2text.textualize_post(url)

	expected_output = test_data['expected_output'][0]
	
	assert normalize_text(output) == normalize_text(expected_output)