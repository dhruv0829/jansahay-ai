from typing import Optional
from pydantic import BaseModel

class ProfileBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = "All"
    state: Optional[str] = None
    district: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    social_category: Optional[str] = "General"
    is_rural: Optional[bool] = True
    landholding_acres: Optional[float] = 0.0
    is_disabled: Optional[bool] = False
    has_bpl_card: Optional[bool] = False
    is_student: Optional[bool] = False
    education_level: Optional[str] = None
    minority: Optional[bool] = False

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: int
    user_id: int
    completeness_percentage: int = 0

    class Config:
        from_attributes = True
