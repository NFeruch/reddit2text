import pytest
from reddit2text.main import Reddit2Text
import pandas as pd

@pytest.fixture
def reddit2text():
	return Reddit2Text()

@pytest.fixture
def test_data():
	return pd.read_csv('tests/test_data.csv')

def test_zero_max_comment_depth(reddit2text: Reddit2Text):

def test_reddit2text(reddit2text: Reddit2Text, test_data: pd.DataFrame):
	url = "https://www.reddit.com/r/help/comments/1190q79/how_to_unarchive_my_archived_posts_also_just_why/"
	output = reddit2text.textualize_post(url)

	assert output == test_data['expected_output'][0]
