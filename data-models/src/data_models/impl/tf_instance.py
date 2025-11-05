from data_models.core.base_model import BaseInstance
from data_models.core.base_metadata import BaseMetadata

import numpy as np
from scipy.spatial.transform import Rotation
from typing import Dict, Optional
from data_models.impl.transforms import Transform3D


class TFInstance(BaseInstance):
    """Data model for a single TF transform instance.
    
    Attributes
    ----------
    transforms : Dict[str, Transform3D]
        Dictionary mapping child_frame_id to TransformData
    metadata : BaseMetadata
        Metadata containing timestamp and index
    """
    
    transforms : Dict[str, Transform3D]
    metadata : BaseMetadata

    class Config:
        arbitrary_types_allowed = True

    @property
    def timestamp(self) -> float:
        """Get the timestamp for this TF instance.
        
        Returns
        -------
        float
            Timestamp in seconds
        """
        return self.metadata.timestamp
    
    @property
    def index(self) -> int:
        """Get the index for this TF instance.
        
        Returns
        -------
        int
            Index of this instance
        """
        return self.metadata.index
    
    def get_transform(self, child_frame_id: str) -> Optional[Transform3D]:
        """Get transform data for a specific child frame.
        
        Parameters
        ----------
        child_frame_id : str
            The child frame ID to look up
            
        Returns
        -------
        Optional[Transform3D]
            Transform data if found, None otherwise
        """
        return self.transforms.get(child_frame_id)
    
    def has_frame(self, child_frame_id: str) -> bool:
        """Check if a specific child frame exists in this TF instance.
        
        Parameters
        ----------
        child_frame_id : str
            The child frame ID to check
            
        Returns
        -------
        bool
            True if the frame exists, False otherwise
        """
        return child_frame_id in self.transforms

