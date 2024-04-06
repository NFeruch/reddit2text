from setuptools import setup, find_packages

VERSION = '0.0.4'  # Consider starting with a semantic versioning scheme
DESCRIPTION = 'Convert Reddit posts to text'
LONG_DESCRIPTION = """
A Python package for converting Reddit posts into structured text representations.
This includes the post's title, author, upvotes, and body, along with all comments
and their hierarchical structure. Ideal for processing, analysis, or feeding into
natural language models.
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
        'praw',  # Ensure you have listed all necessary dependencies
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
