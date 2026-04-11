from pydantic import BaseModel

class Parameters(BaseModel):
    minThresh: int
    maxThresh: int
    blur_kernel: int
    morph_kernel: int
    xFactor:float
    yFactor:float