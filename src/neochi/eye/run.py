import redis
from neochi.eye import settings
from neochi.eye import start_capture


if __name__ == "__main__":
    r = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, db=0)
    start_capture(settings.SIZE, r, fps=settings.FPS)