import redis
import json
from datetime import datetime, timedelta
from api.service_layer import unit_of_work

# Initialize a Redis client, which should be
# bootstraped instead
r = redis.Redis(host='localhost', port=6379, db=0)


def check_minute_passed(user_id, timestamp):
    pipe = r.pipeline()
    pipe.lindex(user_id, -1)
    pipe.exists(user_id)
    result = pipe.execute()
    oldest_timestamp_str = result[0] and json.loads(result[0])["timestamp"]
    oldest_timestamp = oldest_timestamp_str and datetime.fromisoformat(
        oldest_timestamp_str)
    if oldest_timestamp and timestamp - oldest_timestamp >= timedelta(minutes=1):
        return True
    return False


def add_entry_to_buffer(user_id, timestamp, lat, long, accuracy, speed):
    timestamp_str = timestamp.isoformat()
    # 2017-08-01 06:37:00 i had a bug with this one :^)
    if timestamp_str.startswith("2017-08-01T06:37"):
        print("I really want to debug this one")
    # Begin a Redis transaction
    pipe = r.pipeline()
    pipe.sismember(f"{user_id}:timestamps", timestamp_str)
    result = pipe.execute()
    if not result[0] and timedelta:
        location = {
            "timestamp": timestamp.isoformat(),
            "lat": lat,
            "long": long,
            "accuracy": accuracy,
            "speed": speed,
            "user_id": user_id,
        }
        pipe = r.pipeline()
        pipe.lpush(user_id, json.dumps(location))
        pipe.sadd(f"{user_id}:timestamps", timestamp_str)
        pipe.execute()


async def check_timestamp_is_newer(user_id, timestamp,
                                   uow: unit_of_work.AbstractUnitOfWork):
    pipe = r.pipeline()
    pipe.lindex(user_id, 0)
    pipe.exists(user_id)
    result = pipe.execute()
    if result[0] is not None:
        newest_timestamp_str = result[0] and json.loads(result[0])["timestamp"]
        if newest_timestamp_str:
            newest_timestamp = datetime.fromisoformat(newest_timestamp_str)
            if timestamp > newest_timestamp:
                return True
            return False
    else:
        # Nothing? find in db
        current = await uow.locations.get_last_location_for_user(user_id)
        if current:
            if timestamp > current.timestamp:
                return True
            return False
        return True
