from reddit2text import Reddit2Text
from datetime import datetime

r2t = Reddit2Text(
    # replace with your actual creds
    client_id="",
    client_secret="",
    user_agent=""
)

def get_unix_time(date_str):
    date_format = "%Y-%m-%d %H:%M:%S"  # Adjust this format based on the expected input
    dt = datetime.strptime(date_str, date_format)
    unix_time = int(dt.timestamp())
    return unix_time

def get_user_input(prompt, input_type=str, default=None):
    user_input = input(prompt)
    if user_input:
        if input_type == bool:
            return user_input.lower() in ('yes', 'true', 't', '1')
        return input_type(user_input)
    return default

# Store user inputs in a dictionary
inputs = {
    'min_upvotes': get_user_input('Enter minimum upvotes (press enter to skip): ', int, None),
    'max_upvotes': get_user_input('Enter maximum upvotes (press enter to skip): ', int, None),
    'min_length': get_user_input('Enter minimum length of comments (press enter to skip): ', int, None),
    'max_length': get_user_input('Enter maximum length of comments (press enter to skip): ', int, None),
    'min_time': get_user_input('Enter minimum date and time (YYYY-MM-DD HH:MM:SS, press enter to skip): ', str, None),
    'max_time': get_user_input('Enter maximum date and time (YYYY-MM-DD HH:MM:SS, press enter to skip): ', str, None),
    'filter_text': get_user_input('Enter text to filter comments (press enter to skip): ', str, None),
    'filter_author': get_user_input('Enter author to filter comments (press enter to skip): ', str, None),
    'submitter': get_user_input('Filter comments by submitter (True/False, press enter to skip): ', bool, None)
}

# Initialize sorting parameters to None
inputs['score_sort_order'] = None
inputs['length_sort_order'] = None
inputs['time_sort_order'] = None

# Ask user for sorting preference and set the appropriate sorting parameter
sort_preference = get_user_input('Enter sorting preference (score/length/time, press enter to skip): ', str, None)
if sort_preference == 'score':
    inputs['score_sort_order'] = get_user_input('Enter score sort order (ascending/descending): ', str)
elif sort_preference == 'length':
    inputs['length_sort_order'] = get_user_input('Enter length sort order (ascending/descending): ', str)
elif sort_preference == 'time':
    inputs['time_sort_order'] = get_user_input('Enter time sort order (ascending/descending): ', str)

# Convert time to unix-time
if inputs['min_time'] is not None:
    inputs['min_time'] = get_unix_time(inputs['min_time'])
if inputs['max_time'] is not None:
    inputs['max_time'] = get_unix_time(inputs['max_time'])

# Replace post URL
URL = ""
output = r2t.textualize_post(URL, **inputs)
print(output)
