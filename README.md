# Tweefee

Tweefee is a Tornado-based web application that streams tweets for a given search query right to the browser in clean
and elegant way. The app uses Twitter Streaming API and websockets.

The motivation behind Tweefee was to use it on community events in order to show tweets to the audience in realtime.

## Installation

The app runs on Python 3. It's recommended to run it in Python virtual environment. 

The app is not intended to use via pypi. In order to start using Tweefee just (fork and) clone the repo:
 
`$ git clone git@github.com:haxoza/tweefee.git`

Then enter to the project directory and install dependencies:

`$ pip install -r requirements.txt`

Now you need to [set up Twitter app](https://apps.twitter.com/) in order to get API keys to be able to
query Twitter API.

Then you also need access token. To get it you should go into Twitter app details, choose Key and Access Tokens tab
and click generate access token button.

## Usage

The application is designed as two separate programs that should be run in parallel. The first one is Tronado
application that receive tweets via REST API from the second program and sends them to the connected users via
websocket.

To run Tornado app locally type:

`$ python tweefee/tweefee.py --debug --logging=info`

and then run Twitter listener:

`$ python tweefee/listener.py --api_key <API_KEY> --api_secret <API_SECRET> --access_token <ACCESS_TOKEN> --access_token_secret <ACCESS_TOKEN_SECRET> --hash_tags "#selfie" --logging=info`

where variables in `<>` can be found in your [Twitter application settings](https://apps.twitter.com/).

If you passed API keys and access token to the listener app properly you can open the app in your browser using
the address `127.0.0.1:8888`.   

To see help messages you can pass `--help` option to both applications.

For production usage do not pass `--debug` option to Tornado app.
