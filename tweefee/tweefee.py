import logging
import os
import collections
from tornado import escape, gen, ioloop, web, websocket
from tornado.options import OptionParser


class IndexHandler(web.RequestHandler):

    def initialize(self, **context):
        self.context = context
        self.context['websocket_path'] = self.application.reverse_url('websocket')

    def get(self):
        self.render('index.html', **self.context)


class TweetWebSocketHandler(websocket.WebSocketHandler):
    waiters = set()

    def initialize(self, history):
        self.history = history
        self.logger = logging.getLogger(type(self).__name__)

    def check_origin(self, origin):
        return True

    def open(self):
        self.waiters.add(self)
        self.logger.info('Connection opened. Waiters: {}.'.format(len(self.waiters)))
        self.send_history()

    def on_close(self):
        self.logger.info('Connection closed.')
        self.waiters.remove(self)

    @classmethod
    @gen.coroutine
    def send_updates(cls, tweets):
        data = escape.json_encode(tweets)
        for waiter in cls.waiters:
            try:
                waiter.write_message(data)
                yield gen.moment
            except websocket.WebSocketClosedError:
                logging.error('Error sending message.', exc_info=True)

    def send_history(self):
        data = escape.json_encode(list(self.history))
        self.write_message(data)


class APIHandler(web.RequestHandler):

    def initialize(self, history, allowed_host):
        self.history = history
        self.allowed_host = allowed_host
        self.logger = logging.getLogger(type(self).__name__)

    def check_origin(self):
        return self.request.headers.get('Host').startswith(self.allowed_host)

    @gen.coroutine
    def post(self, *args, **kwargs):
        self.set_status(201)
        self.finish()
        if self.check_origin():
            self.process()

    @gen.coroutine
    def process(self):
        try:
            data = escape.json_decode(self.request.body)
        except ValueError:
            self.logger.error('Malformed data received.')
        else:
            self.history.extendleft(data)
            yield TweetWebSocketHandler.send_updates(data)


def load_config():
    options = OptionParser()
    options.define('port', default=8888, help='run on the given port', type=int)
    options.define('debug', default=False, help='run in debug mode')
    options.define('api_allowed_host', default='localhost', help='origin host that has access to API')
    options.define('history_size', default=50, help='number of tweets stored in memoty', type=int)
    options.define('config', type=str, help='path to config file',
                   callback=lambda path: options.parse_config_file(path, final=False))
    options.define('logging', default='error', help='logging level')
    options.parse_command_line()
    return options


def main():
    options = load_config()
    logging.basicConfig(level=logging.getLevelName(options.logging.upper()))
    history = collections.deque(maxlen=options.history_size)
    app = web.Application(
        [
            (r'/', IndexHandler, dict(history=history)),
            (r'/websocket', TweetWebSocketHandler, dict(history=history), 'websocket'),
            (r'/api', APIHandler, dict(history=history, allowed_host=options.api_allowed_host)),
        ],
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        debug=options.debug,
        static_hash_cache=True,
        compiled_template_cache=True,
    )
    app.listen(options.port)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
