
import os

import redis
from rq import Worker, Queue, Connection

listen = ['default']

if not os.getenv('OPENAI_API_KEY'):
    print('Error: OpenAI API key is not set.')
    exit()

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
