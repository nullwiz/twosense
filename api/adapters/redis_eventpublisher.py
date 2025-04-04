import json
import redis.asyncio as redis
import logging
from api import config
import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


async def publish(channel: str, event: str, data: dict):
    logger.info(f"Publishing {event} to {channel}")
    await r.publish(channel, json.dumps({"event": event, "data": data},
                                        cls=DateTimeEncoder))
    logger.info(f"Published {event} to {channel}")
