from rclpy.time import Time
from builtin_interfaces.msg import Time as BuiltinTime

from typing import Union

def time_to_timestamp(time : Union[Time, BuiltinTime]) -> float:

    if isinstance(time, Time):
        seconds, nanoseconds = time.seconds_nanoseconds()
    else:
        seconds, nanoseconds = time.sec, time.nanosec

    time = seconds + (nanoseconds * 1e-9)

    return time

def timestamp_to_time(timestamp : float) -> BuiltinTime:

    return BuiltinTime(sec=int(timestamp),
                       nanosec=int((timestamp - int(timestamp)) * 1e9))