from data_models.core.base_metadata import BaseMetadata
from data_models.core.base_model import BaseInstance

from pydantic import BaseModel, ConfigDict
import numpy as np

from typing import Generator, List

class DataStream(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __len__(self) -> int:
        """Returns the number of instances in the data stream.

        Returns
        -------
        int
            The total number of instances in this data stream.
        """
        return len(self.timestamps)

    def duration(self) -> float:
        """Returns the total duration of the data stream in seconds.

        The duration is calculated as the difference between the last and first 
        timestamps in the stream. If the stream is empty, returns 0.

        Returns
        -------
        float
            The duration of the data stream in seconds.
        """
        
        timestamps = self.timestamps
        if len(timestamps) == 0:
            return 0

        return self.end_time - self.start_time

    def iterate(self, skip_every: int = 1) -> Generator[BaseInstance, None, None]:
        """Iterate through instances in the data stream.

        This method yields instances from the data stream sequentially.

        Yields
        -------
        BaseInstance
            Sequential instances from the data stream.

        Notes
        -----
        The instances are yielded in chronological order based on their timestamps.
        """
        return map(
            self.get_instance,
            range(0, len(self), skip_every)
        )
    
    def get_instance(self, index : int) -> BaseInstance:
        """Get a BaseInstance from the data stream at the specified index.

        Parameters
        ----------
        index : int
            Index of the instance to retrieve. Negative indices are supported and count from the end.

        Returns
        -------
        BaseInstance
            The instance at the specified index.

        Notes
        -----
        This method first gets the instance metadata using get_instance_metadata(), then creates and returns
        the actual instance using make_instance().
        """

        instance_metadata = self.get_instance_metadata(index)

        return self.make_instance(instance_metadata)
    
    def get_instance_metadata(self, index : int) -> BaseMetadata:
        """Get metadata for a instance at the specified index.

        Parameters
        ----------
        index : int
            Index of the instance to retrieve metadata for. Negative indices are supported and count from the end.

        Returns
        -------
        BaseMetadata
            Metadata object containing the index and timestamp.

        Notes
        -----
        This method handles negative indexing by converting negative indices to their positive equivalents.
        The returned metadata includes both the index and its associated timestamp from the data stream.
        """

        if index < 0:
            index = len(self) + index

        return BaseMetadata(
            index=index,
            timestamp=self.timestamps[index]
        )


    def get_previous_instance_metadata(self, timestamp : float) -> BaseMetadata:
        """Get metadata for the instance immediately before the specified timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the previous instance for.

        Returns
        -------
        BaseMetadata
            Metadata for the instance immediately before the specified timestamp.

        Notes
        -----
        This method:
        1. Finds the index of the instance before the timestamp
        2. Returns the metadata for that instance
        """
    
        index = self._find_previous_timestamp_index(timestamp)
        return self.get_instance_metadata(index)
    
    def get_next_instance_metadata(self, timestamp : float) -> BaseMetadata:
        """Get metadata for the instance immediately after the specified timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the next instance for.

        Returns
        -------
        BaseMetadata
            Metadata for the instance immediately after the specified timestamp.

        Notes
        -----
        This method:
        1. Finds the index of the instance after the timestamp
        2. Returns the metadata for that instance
        """

        index = self._find_next_timestamp_index(timestamp)
        return self.get_instance_metadata(index)

    def get_nearest_instance_metadata(self, timestamp : float) -> BaseMetadata:
        """Get metadata for the instance nearest to the specified timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the nearest instance for.

        Returns
        -------
        BaseMetadata
            Metadata for the instance closest in time to the specified timestamp.

        Notes
        -----
        This method:
        1. Finds the index of the instance nearest to the timestamp
        2. Returns the metadata for that instance
        """

        index = self._find_nearest_timestamp_index(timestamp)
        return self.get_instance_metadata(index)
        
    def get_previous_instance(self, timestamp : float) -> BaseInstance:
        """Get the instance immediately before the specified timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the previous instance for.

        Returns
        -------
        BaseInstance
            The snapshot immediately before the specified timestamp.

        Notes
        -----
        This method:
        1. Gets metadata for the instance before the timestamp
        2. Creates and returns a instance from that metadata
        """
        return self.make_instance(self.get_previous_instance_metadata(timestamp))


    def get_next_instance(self, timestamp : float) -> BaseInstance:
        """Get the instance immediately after the specified timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the next instance for.

        Returns
        -------
        BaseInstance
            The snapshot immediately after the specified timestamp.

        Notes
        -----
        This method:
        1. Gets metadata for the next instance after the timestamp
        2. Creates and returns a instance from that metadata
        """
        return self.make_instance(self.get_next_instance_metadata(timestamp))
    
    def get_nearest_instance(self, timestamp : float) -> BaseInstance:
        """Get the snapshot closest in time to the specified timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the nearest instance for.

        Returns
        -------
        BaseInstance
            The instance closest in time to the specified timestamp.

        Notes
        -----
        This method:
        1. Gets metadata for the instance nearest to the timestamp
        2. Creates and returns a instance from that metadata
        """
        return self.make_instance(self.get_nearest_instance_metadata(timestamp))

    def make_instance(self, instance_metadata : BaseMetadata) -> BaseInstance:
        """Function for creating a instance. Must be implemented in subclasses.

        Args:
            instance_metadata (BaseMetadata): A data structure containing necessary
                metadata for making the instance

        Raises:
            NotImplementedError: Override this implementation in subclasses

        Returns:
            BaseModel: A instance containing relevant data, must be subclass of BaseModel
        """
        raise NotImplementedError

    @property
    def start_time(self) -> float:
        """Get the timestamp of the first instance in the data stream.

        Returns
        -------
        float
            The timestamp of the first instance, or 0 if the stream is empty.

        Notes
        -----
        This property provides access to the timestamp of the first instance in the data stream.
        If the stream is empty (has no instances), it returns 0.
        """
        
        if len(self.timestamps) == 0:
            return 0
        
        return self.timestamps[0]
        
    @property
    def end_time(self) -> float:
        """Get the timestamp of the last instance in the data stream.

        Returns
        -------
        float
            The timestamp of the last instance, or 0 if the stream is empty.

        Notes
        -----
        This property provides access to the timestamp of the last instance in the data stream.
        If the stream is empty (has no instances), it returns 0.
        """
        
        if len(self.timestamps) == 0:
            return 0
        
        return self.timestamps[-1]

    @property
    def resolution(self) -> float:
        """Get the median time interval between consecutive instances.

        Returns
        -------
        float
            The median time difference between consecutive instances in seconds.
            Returns 0 if the stream is empty.

        Notes
        -----
        This property calculates the temporal resolution of the data stream by finding
        the median time difference between consecutive instances. This provides a
        measure of the typical sampling rate of the data.
        """
        
        if len(self.timestamps) == 0:
            return 0
        
        return np.median(np.diff(self.timestamps))

    @property
    def timestamps(self) -> List[float]:
        """Get the list of timestamps for all instances in the data stream.

        Returns
        -------
        List[float]
            A list of timestamps in chronological order, one for each instance in the stream.

        Notes
        -----
        This property must be implemented by subclasses to provide access to the timestamps
        of all instances in their data stream. The timestamps should be returned as a list
        of float values representing seconds.
        """
        raise NotImplementedError
    

    def is_empty(self) -> bool:
        """Check if the data stream is empty.

        Returns
        -------
        bool
            True if the data stream contains no instances, False otherwise.

        Notes
        -----
        A data stream is considered empty if it has no timestamps associated with it.
        """
        return len(self.timestamps) == 0




    def _find_previous_timestamp_index(self, timestamp : float) -> int:
        """Find the index of the instance immediately before the given timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the previous instance for.

        Returns
        -------
        int
            Index of the instance immediately before the given timestamp.

        Notes
        -----
        This method uses numpy's searchsorted to efficiently find the insertion point
        for the timestamp, then adjusts the index to get the previous instance.
        The returned index will point to the last instance that occurred before
        the given timestamp.
        """

        index = np.searchsorted(self.timestamps, timestamp)
        
        # Necessary to get previous snapshot index
        if (index > 0):
            index = index - 1

        return index
    
    def _find_next_timestamp_index(self, timestamp : float) -> int:
        """Find the index of the snapshot immediately after the given timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the next snapshot for.

        Returns
        -------
        int
            Index of the snapshot immediately after the given timestamp.

        Notes
        -----
        This method uses numpy's searchsorted to efficiently find the insertion point
        for the timestamp. The returned index will point to the first instance that
        occurred after the given timestamp, unless the timestamp is after the last
        instance in which case it returns the last instance index.
        """

        index = np.searchsorted(self.timestamps, timestamp)

        if (index == len(self)):
            index = index - 1

        return index

    def _find_nearest_timestamp_index(self, timestamp : float) -> int:
        """Find the index of the instance with timestamp closest to the given timestamp.

        Parameters
        ----------
        timestamp : float
            The timestamp to find the nearest instance for.

        Returns
        -------
        int
            Index of the instance with timestamp closest to the given timestamp.

        Notes
        -----
        This method finds both the previous and next instance indices relative to the
        given timestamp, then returns whichever one has a timestamp closer to the
        target timestamp. If the differences are equal, the next instance index is returned.
        """

        previous_index = self._find_previous_timestamp_index(timestamp)
        next_index = self._find_next_timestamp_index(timestamp)

        previous_timestamp = self.timestamps[previous_index]
        next_timestamp = self.timestamps[next_index]

        previous_diff = timestamp - previous_timestamp
        next_diff = next_timestamp - timestamp

        if (previous_diff < next_diff):
            return previous_index
        else:
            return next_index