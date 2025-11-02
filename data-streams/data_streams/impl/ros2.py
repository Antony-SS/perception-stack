
from ..core import DataStream
from data_models.core.base_model import BaseModel
from data_models.core.base_metadata import BaseMetadata
from ros_message_conversions.ros2.time_funcs import time_to_timestamp, timestamp_to_time

from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore, get_types_from_msg
from rosbags.typesys.store import Typestore
from rclpy.time import Time

from typing import Callable, Optional, Any, List, Tuple

class Ros2DataStream(DataStream):

    ros2_mcap_path : str
    loaded_ros2_mcap_reader : Optional[Reader]
    decode_fn : Callable[[Any, int, float], BaseModel]
    topic : str
    interpolable : bool
    use_header_timestamps : bool
    _timestamps : Optional[List[float]] = None
    _raw_timestamps : Optional[List[float]] = None
    connection : Optional[Any] = None
    connections : Optional[List[Any]] = None
    typestore : Optional[Typestore] = None

    def __init__(__pydantic_self__, **data):

        super().__init__(**data)
        self = __pydantic_self__

        if self.loaded_ros2_mcap_reader is None:
            self.loaded_ros2_mcap_reader = Reader(self.ros2_mcap_path)
        self.loaded_ros2_mcap_reader.open()

        self.connections = [
            x for x in self.loaded_ros2_mcap_reader.connections if x.topic == self.topic
        ]
        if len(self.connections) > 0:
            self.connection = self.connections[0]
        else:
            return

        self.typestore = get_typestore(Stores.LATEST)
        self.typestore.register(
            get_types_from_msg(
                self.connection.msgdef, 
                self.connection.msgtype
            )
        )


        #self._timestamps = self.get_timestamps()

    def make_instance(self, instance_metadata : BaseMetadata) -> BaseModel:

        topic, msg, time = self.get_message(instance_metadata)

        return self.decode_fn(
            msg,
            instance_metadata.index,
            instance_metadata.timestamp,
        )
    
    @property
    def timestamps(self) -> List[float]:
        if not self._timestamps:
            self._timestamps, self._raw_timestamps = self.get_timestamps()

        return self._timestamps

    def get_timestamps(self) -> Tuple[List[float], List[float]]:

        # Real timestamps and raw timestamps will not match, if header is being used
        timestamps = []
        raw_timestamps = []

        # Handle edge cases
        if self.connection is None or self.connections is None or len(self.connections) == 0:
            return timestamps

        # Iterate through all timestamps in MCAP
        for i, (conn, raw_timestamp, data) in enumerate(self.loaded_ros2_mcap_reader.messages(
            connections=[self.connection]
        )):
            
            # Convert raw timestamp to seconds from nanoseconds
            raw_timestamp = raw_timestamp * 1e-9
            
            # Handle header, if relevant
            if self.use_header_timestamps:
                deserialized_message = self.typestore.deserialize_cdr(data, conn.msgtype)
                timestamp = time_to_timestamp(deserialized_message.header.stamp)
            
            # timestamp is equal to raw_timestamp if header is not used
            else:
                timestamp = raw_timestamp

            # Append timestamps
            timestamps.append(timestamp)
            raw_timestamps.append(raw_timestamp)

        return timestamps, raw_timestamps
    
    def get_message(self, instance_metadata : BaseMetadata) -> Tuple[str, Any, Time]:

        # Create initial time by sampling from raw timestamps, then shifting down by small amount
        start_time = self._raw_timestamps[instance_metadata.index] - 1e-6

        # Convert to nanoseconds
        timestamp_ns = int(start_time * 1e9)

        # Query message from MCAP reader
        conn, ts, data = next(self.loaded_ros2_mcap_reader.messages(
            connections=[self.connection],
            start=timestamp_ns
        ))

        # Deserialize message
        message = self.typestore.deserialize_cdr(data, conn.msgtype)

        return conn, message, ts

def make_ros2_mcap_data_stream(ros2_mcap_path : str,
                               loaded_mcap : Optional[Reader],
                               topic : str,
                               decode_fn : Callable[[Any, int, float], BaseModel],
                               interpolable : bool,
                               use_header_timestamps : bool) -> Ros2DataStream:
    
    return Ros2DataStream(
        ros2_mcap_path=ros2_mcap_path,
        loaded_ros2_mcap_reader=loaded_mcap,
        decode_fn=decode_fn,
        topic=topic,
        interpolable=interpolable,
        use_header_timestamps=use_header_timestamps
    )