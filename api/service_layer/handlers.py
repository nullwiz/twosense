from __future__ import annotations
from dataclasses import asdict
from api.domain import events, models, commands
from api.adapters import redis_eventpublisher
from api.service_layer import unit_of_work
from api.config import get_redis_host_and_port
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz
import pandas as pd
import redis
import json


# This needs some cleanup, with more time I would have moved some of these functions
# to their own files, for example:
# utils/redis_ops.py, utils/timezone.py
# utils/data_resampling.py

tf = TimezoneFinder()

# Initialize a Redis client
r = redis.Redis(host=get_redis_host_and_port()["host"],
                port=get_redis_host_and_port()["port"],
                db=0, decode_responses=True)


def convert_to_utc(timestamp, lat, long):
    print("Converting to UTC, timestamp: ", timestamp)
    print("coordinates: ", lat, long)
    tz_str = tf.timezone_at(lng=long, lat=lat)
    local_tz = pytz.timezone(tz_str)

    if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None:
        local_time = local_tz.localize(timestamp)
    else:
        local_time = timestamp

    utc_time = local_time.astimezone(pytz.UTC)
    print(utc_time)
    print(utc_time.tzinfo)
    utc_time = utc_time.replace(tzinfo=None)
    return utc_time


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
        print("awesome, a breakpoint!")
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
        # Begin a new transaction to add the entry
        pipe = r.pipeline()
        pipe.lpush(user_id, json.dumps(location))
        pipe.sadd(f"{user_id}:timestamps", timestamp_str)
        pipe.execute()


async def check_timestamp_is_newer(user_id, timestamp,
                                   uow: unit_of_work.AbstractUnitOfWork):
    pipe = r.pipeline()
    # Check newest data in redis
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
        # Check newest data in db
        current = await uow.locations.get_last_location_for_user(user_id)
        if current:
            if timestamp > current.timestamp:
                return True
            return False
        return True


def mean_df_resample(df):
    df.set_index('timestamp', inplace=True)
    df.drop('user_id', axis=1, inplace=True)
    df_resampled = df.resample('1T').mean()
    return df_resampled


async def put_location(cmd: commands.PutLocation, uow: unit_of_work.AbstractUnitOfWork):
    user_id = cmd.user_id
    async with uow:
        utc_time = convert_to_utc(cmd.timestamp, cmd.lat, cmd.long)
        if check_minute_passed(user_id, utc_time):
            buffer_data = [json.loads(i) for i in r.lrange(user_id, 0, -1)]
            for entry in buffer_data:
                entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
            timestamp = mean_df_resample(pd.DataFrame(buffer_data)).index[0]
            existing_timestamp = await uow.locations.get_location_by_timestamp(user_id,
                                                                               timestamp)
            # I want only one record in the db for each minute, so I resample the data
            if existing_timestamp:
                buffer_data.append({
                    "timestamp": existing_timestamp.timestamp,
                    "lat": existing_timestamp.lat,
                    "long": existing_timestamp.long,
                    "accuracy": existing_timestamp.accuracy,
                    "speed": existing_timestamp.speed,
                    "user_id": existing_timestamp.user_id,
                })
                # delete it, we are going to be adding one with the new mean
                await uow.locations.delete(existing_timestamp)

            df_resampled = mean_df_resample(pd.DataFrame(buffer_data))
            pipe = r.pipeline()
            pipe.delete(user_id)
            pipe.delete(f"{user_id}:timestamps")
            pipe.execute()
            for timestamp, row in df_resampled.iterrows():
                location = models.Location(
                    timestamp=timestamp,
                    lat=row["lat"],
                    long=row["long"],
                    accuracy=row["accuracy"],
                    speed=row["speed"],
                    user_id=user_id
                )
                await uow.locations.add(location)
            await uow.commit()
            for timestamp, row in df_resampled.iterrows():
                location = models.Location(
                    timestamp=timestamp,
                    lat=row["lat"],
                    long=row["long"],
                    accuracy=row["accuracy"],
                    speed=row["speed"],
                    user_id=user_id
                )
                await publish_location_added_event(location)
        else:
            new_timestamp = await check_timestamp_is_newer(user_id, utc_time, uow)
            if new_timestamp:
                add_entry_to_buffer(user_id, utc_time, cmd.lat,
                                    cmd.long, cmd.accuracy, cmd.speed)


async def publish_location_added_event(location: models.Location):

    event = events.LocationAdded(
        timestamp=location.timestamp.isoformat(),
        lat=location.lat,
        long=location.long,
        accuracy=location.accuracy,
        speed=location.speed,
        user_id=location.user_id,
    )
    await redis_eventpublisher.publish(channel="locations",
                                       event="LocationAdded", data=asdict(event))


async def healthcheck_handler(cmd: commands.HealthCheck,
                              uow: unit_of_work.AbstractUnitOfWork):
    async with uow:
        await uow.commit()
        return True

EVENT_HANDLERS = {
    events.LocationAdded: [publish_location_added_event],
}

COMMAND_HANDLERS = {
    commands.PutLocation: put_location,
    commands.HealthCheck: healthcheck_handler,
}
