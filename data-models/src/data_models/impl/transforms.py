import numpy as np
from scipy.spatial.transform import Rotation

from pydantic import BaseModel

class Transform3D(BaseModel):
    translation: np.ndarray
    rotation: Rotation

    class Config:
        arbitrary_types_allowed = True

    def euler_flu_degrees(self) -> np.ndarray: #TODO: Add support for other conventions
        return self.rotation.as_euler('xyz', degrees=True)

