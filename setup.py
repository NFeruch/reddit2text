# clear && python3 setup.py sdist bdist_wheel && twine upload --skip-existing dist/* --verbose
from setuptools import setup, find_packages

VERSION = '0.0.9'  # Consider starting with a semantic versioning scheme
DESCRIPTION = 'Convert Reddit posts to text'
LONG_DESCRIPTION = """
# Reddit2Text

`reddit2text` is *the* Python library designed to effortlessly **transform any Reddit thread into clean, readable text data**.

Perfect for *feeding to an LLM, performing textual/data analysis, or simply archiving for offline use*, `reddit2text` offers a straightforward interface to access and convert content from Reddit.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quickstart](#quickstart)
  - [Example Code](#example)
  - [Example Output](#output)
- [Configs](#configs)
- [Contributions](#contributions)
- [License](#license)

<a id="features"></a>

## Features
- Convert any Reddit thread (the post + all its comments) into structured text.
- Include all comments, with the ability to specify the maximum comment depth.
- Configure a custom comment delimiter, for visual separation of nested comments.

> **Have a Feature Idea?**
>
> Simply ***open an issue on github*** and tell us what should be added to the next release!

<a id="installation"></a>

## Installation
Easy install using pip
```sh
pip3 install reddit2text
```

<a id="quickstart"></a>

## Quickstart
**First**, you need to create a Reddit app to get your **client_id** and **client_secret**. Follow the instructions on [Reddit's API documentation](https://www.reddit.com/wiki/api) to set up your application.

**Then**, replace the `client_id`, `client_secret`, and `user_agent` with your credentials.

The user agent can be anything you like, but we recommend following this convention according to Reddit's guidelines: `'<app type>:<app name>:<version> (by <your username>)'`

<a id="example"></a>

*Here's an example:*
```python
from reddit2text import Reddit2Text

r2t = Reddit2Text(
    # example credentials
    client_id='123abc',
    client_secret='123abc',
    user_agent='script:my_app:v1.0 (by u/reddit2text)'
)

# The URL must have the post ID after the /comments/ to work, e.g. `1buyr0g`
URL = 'https://www.reddit.com/r/MadeMeSmile/comments/1buyr0g/ryan_reynolds_being_wholesome/'

output = r2t.textualize_post(URL)
print(output)
```

<a id="output"></a>

Here is an example (truncated) output from the above code!
https://pastebin.com/mmHFJtcc

<a id="configs"></a>

## Extra Configuration
- **max_comment_depth**: Maximum depth of comments to output. Includes the top-most comment. Defaults to `None` or `-1` to include all.
- **comment_delim**: String/character used to indent comments according to their nesting level. Defaults to `|` to mimic reddit.

```python
r2t = Reddit2Text(
    # credentials ...
    max_comment_depth=3,  # all comment chains will be limited to a max of 3 replies
    comment_delim='#'  # each comment level will be preceded by multiples of this string
)
```

<a id="contributions"></a>

## Contributions
Contributions to reddit2text are welcome. Please submit pull requests or issues to our GitHub repository.

<a id="license"></a>

## License
reddit2text is released under the MIT License. See the LICENSE file for more details.
"""

# Setting up
setup(
    name="reddit2text",
    version=VERSION,
    author="Nicholas Hansen-Feruch",
    author_email="nicholas.feruch@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',  # Specify the LONG_DESCRIPTION is in Markdown
    packages=find_packages(),
    install_requires=[
        'praw',
    ],
    keywords=['python', 'reddit', 'text conversion', 'reddit api', 'praw', 'reddit to text', 'reddit comments', 'social media analysis'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",  # Updated to reflect a more accurate audience
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",  # Specify Python 3, as Python 2 is deprecated
        "License :: OSI Approved :: MIT License",  # Specify your license
        "Operating System :: OS Independent",  # If your package is OS independent
    ],
    python_requires='>=3.6',  # Specify the Python version requirements
)
