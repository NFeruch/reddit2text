# Reddit2Text

`reddit2text` is *the* Python library designed to effortlessly **transform any Reddit thread into clean, readable text data**.

Perfect for *feeding to an LLM, performing textual/data analysis, or simply archiving for offline use*, `reddit2text` offers a straightforward interface to access and convert content from Reddit.

## Table of Contents
- [Installation](#installation)
- [Quickstart](#quickstart)
  - [Example Code](#example)
  - [Example Output](#output)
- [Extra Settings](#configs)
- [Current Features](#features)
- [Planned Features](#planned)
- [Contributions](#contributions)
- [License](#license)

<a id="installation"></a>

## Installation
Easy install using pip
```sh
pip3 install reddit2text
```

<a id="quickstart"></a>

## Quickstart
==**First**, you need to create a Reddit app to get your **client_id** and **client_secret**, in order to access the Reddit API.==
> Here's a [visual step-by-step guide I created](https://scribehow.com/shared/Create_your_Reddit_API_app__sanm5Eo2Q_iudzfhFZLKJg) to do this! Alternatively, you can look at [Reddit's API documentation](https://www.reddit.com/wiki/api).


**Then**, replace the `client_id`, `client_secret`, and `user_agent` with your credentials.

The user agent can be anything you like, but we recommend following this convention according to Reddit's guidelines: `'<app type>:<app name>:<version> (by <your username>)'`

<a id="example"></a>

***This is enough to get started:***
```python
from reddit2text import Reddit2Text

r2t = Reddit2Text(
    # replace with your actual creds
    client_id='123abc',
    client_secret='123abc',
    user_agent='script:my_app:v1.0 (by u/reddit2text)'
)

URL = 'https://www.reddit.com/r/MadeMeSmile/comments/1buyr0g/ryan_reynolds_being_wholesome/'

output = r2t.textualize_post(URL)
print(output)
```

<a id="output"></a>

Here is an example (truncated) output from the above code!
https://pastebin.com/mmHFJtcc

<a id="configs"></a>

## Extra Configuration
- **max_comment_depth**, `Optional[str]`:
  - Maximum depth of comments to output. Includes the top-most comment. Defaults to `None` or `-1` to include all.
- **comment_delim**, `str`:
  - String/character used to indent comments according to their nesting level. Defaults to `|` to mimic reddit.

```python
r2t = Reddit2Text(
    # credentials ...
    max_comment_depth=3,  # all comment chains will be limited to a max of 3 replies
    comment_delim='#'  # each comment level will be preceded by multiples of this string
)
```

<a id="features"></a>

## Current Features
- Convert any Reddit thread (the post + all its comments) into structured text.
- Include all comments, with the ability to specify the maximum comment depth.
- Configure a custom comment delimiter, for visual separation of nested comments.

> **Have a Feature Idea?**
>
> Simply ***open an issue on github*** and tell me what should be added to the next release!

<a id="planned"></a>

## Planned Features
- Comprehensive Formatting/Saving
  - Being able to save to a file location as .txt, .csv, .json, or to your clipboard!
- Filtering/Sorting
  - Filter/sort comments based on upvotes, author name, body content, number of replies, etc. Also add in the ability to get the Top N comments.
- Extra data fields
  - Access extra information for each post/comment, like whether it's NFSW or not and when it was created
- Image/video support
  - Enable mining of not just text threads, but also image and video posts
- CLI output
  - Add a progress bar to the terminal for threads with a large amount of comments
- Anonymize usernames
  - Give the ability to obfuscate usernames, while still preserving their uniqueness across all comments
- Iterate across many posts at once
  - Given a subreddit as the input and the sorting method (hot, top, new, etc.), loop over multiple posts at once and textualize them

<a id="contributions"></a>

## Contributions
Contributions to reddit2text are always welcomed! I'm just a person that made something I think is useful, so any help is appreciated. You can always submit a pull requests or add an issue to the GitHub repository.

<a id="license"></a>

## License
reddit2text is released under the MIT License. See the LICENSE file for more details.
