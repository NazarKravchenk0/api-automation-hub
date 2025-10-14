from rq import Worker, Queue, Connection
from redis import Redis
from app.config import settings

listen = [settings.RQ_QUEUE]

if __name__ == '__main__':
    with Connection(Redis.from_url(settings.REDIS_URL)):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
