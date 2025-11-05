from data_models.core.base_model import BaseInstance
from data_models.core.base_metadata import BaseMetadata
from data_models.impl.transforms import Transform3D

class PoseInstance(BaseInstance):
    """Data model for a single pose instance from odometry.
    
    Attributes
    ----------
    pose : TransformData
        Pose data containing translation and rotation
    metadata : BaseMetadata
        Metadata containing timestamp and index
    """
    
    pose : Transform3D
    metadata : BaseMetadata

    class Config:
        arbitrary_types_allowed = True

    @property
    def timestamp(self) -> float:
        """Get the timestamp for this pose instance.
        
        Returns
        -------
        float
            Timestamp in seconds
        """
        return self.metadata.timestamp
    
    @property
    def index(self) -> int:
        """Get the index for this pose instance.
        
        Returns
        -------
        int
            Index of this instance
        """
        return self.metadata.index
    
    @property
    def translation(self):
        """Get the translation vector.
        
        Returns
        -------
        np.ndarray
            Translation vector [x, y, z]
        """
        return self.pose.translation
    
    @property
    def rotation(self):
        """Get the rotation object.
        
        Returns
        -------
        Rotation
            scipy.spatial.transform.Rotation object
        """
        return self.pose.rotation

