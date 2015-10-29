import argparse
import logging
import requests
import tweepy
from requests.exceptions import RequestException
from tweepy.streaming import StreamListener


class TweeFeedStreamer:

    def __init__(self, api_key, api_secret, access_token, access_token_secret, consumer_url, hash_tags):
        auth = tweepy.auth.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.listener = TweeFeedStreamListener(consumer_url)
        self.stream = tweepy.Stream(auth, self.listener)
        self.hash_tags = hash_tags

    def start_stream(self):
        self.stream.filter(track=self.hash_tags)

    def get_tweets(self, max_count):
        return map(status_to_dict, self.api.search(self.hash_tags[0])[:max_count])


class TweeFeedStreamListener(StreamListener):
    
    def __init__(self, consumer_url):
        super().__init__()
        self.consumer_url = consumer_url
        self.logger = logging.getLogger(type(self).__name__)

    def on_status(self, status):
        self.logger.info('Tweet in stream: {}'.format(status.text))
        data = status_to_dict(status)
        self.send([data])
        return True

    def on_error(self, status_code):
        self.logger.error('Error with status code: {}'.format(str(status_code)))
        return True

    def on_timeout(self):
        self.logger.error('Timeout')
        return True

    def send(self, data):
        try:
            requests.post(self.consumer_url, json=data)
        except RequestException:
            self.logger.error('Cannot send tweet to consumer.')


def status_to_dict(status):
    return {
        'content': status.text,
        'date': status.created_at.isoformat(),
        'id': status.id_str,
        'entities': status.entities,
        'user': {
            'handle': status.user.screen_name,
            'full_name': status.user.name,
            'avatar_url': status.user.profile_image_url,
        }
    }


def load_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_key', type=str, required=True, help='Twitter app api key')
    parser.add_argument('--api_secret', type=str, required=True, help='Twitter app api secret')
    parser.add_argument('--access_token', type=str, required=True, help='access token to Twitter app')
    parser.add_argument('--access_token_secret', type=str, required=True, help='access token secret to Twitter app')
    parser.add_argument('--consumer_url', default='http://localhost:8888/api', help='url to post all received tweets')
    parser.add_argument('--hash_tags', type=str, nargs='+', required=True, help='search terms to observe')
    parser.add_argument('--logging', default='error', help='logging level')
    args = parser.parse_args()
    return args


def main():
    options = load_config()
    logging.basicConfig(level=logging.getLevelName(options.logging.upper()))
    feed = TweeFeedStreamer(
        api_key=options.api_key,
        api_secret=options.api_secret,
        access_token=options.access_token,
        access_token_secret=options.access_token_secret,
        consumer_url=options.consumer_url,
        hash_tags=options.hash_tags,
    )
    feed.listener.send(list(feed.get_tweets(50)))
    feed.start_stream()


if __name__ == '__main__':
    main()
