# Reddit2Text

`reddit2text` is a Python library designed to effortlessly **transform any Reddit post and its comments into a clean, readable text format**.

Perfect for *feeding to an LLM, data analysis, or simply reading offline*, `reddit2text` offers a straightforward interface to access and convert content from Reddit.

## Table of contents
- [Features](#features)
- [Installation](#installation)
- [Quickstart](#quickstart)
  - [Example Code](#example)
- [Configs](#configs)
- [Contributions](#contributions)
- [License](#license)

<a id="features"></a>

## Features
- Convert any Reddit post into structured text format.
- Include all comments, with support for specifying maximum comment depth.
- Configurable comment delimiter for visual separation of nested comments.

> **Want Something Added?**
> Simply ***open an issue*** here on github and tell us what should be added to the next release!

<a id="installation"></a>

## Installation
Install reddit2text using pip
```sh
pip3 install reddit2text
```

<a id="quickstart"></a>

## Quickstart
**First**, you need to register a Reddit application to obtain a **client_id** and **client_secret**. Follow the instructions on [Reddit's API documentation](https://www.reddit.com/wiki/api) to set up your application.

Then, replace the `client_id`, `client_secret`, and `user_agent` with your credentials.

The user agent can be anything you like, but we recommend following this convention that follows Reddit's guidelines: `'<app type>:<app name>:<version> (by <your username>)'`

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

# The URL must have the post ID after the /comments/ to work
URL = 'https://www.reddit.com/r/MadeMeSmile/comments/1buyr0g/ryan_reynolds_being_wholesome/'

output = r2t.textualize_post(URL)
print(output)
```

<a id="configs"></a>

## Extra Configuration
- **max_comment_depth**: Maximum depth of comments to output. Includes the top-most comment. Defaults to `None` or `-1` to include all.
- **comment_delim**: String/character used to indent comments according to their nesting level. Defaults to `|` to mimic reddit.

```python
r2t = Reddit2Text(
    # credentials ...
    max_comment_depth=3,  # all comment trees will be limited to a max of 3 replies
    comment_delim='#'  # each comment level will be preceded by multiples of this string
)
```

<a id="contributions"></a>

## Contributions
Contributions to reddit2text are welcome. Please submit pull requests or issues to our GitHub repository.

<a id="license"></a>

## License
reddit2text is released under the MIT License. See the LICENSE file for more details.
