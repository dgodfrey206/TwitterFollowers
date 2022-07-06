# TwitterFollowers
A Python script for generating the followers and followings of an inputted user. Returns the data as a CSV.

## Requirements

The following are required to run this script:

- Python 3 or later
- Pandas (1.4.2)
- PyYAML (6.0)
- Requests (2.26.0)

This is what you'll need to do if you don't have them:

	pip3 install pandas pyyaml requests

## Getting Started

You will need a Twitter API Bearer token to send to the `config.yaml` file. Go to ![](https://developer.twitter.com) and sign up using your existing Twitter account. After verifying your account and following the steps you'll find your API key, API secret, and Bearer token.

Inside `config.yaml`, copy and paste your bearer token. You'll then be able to run the script.

	python3 followers_following.py 
	Enter a twitter profile username: example
	Looking up user 'example'.
	Found user example with id 1234567.

