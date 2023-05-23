from timezonefinder import TimezoneFinder
import pytz

tf = TimezoneFinder()


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
