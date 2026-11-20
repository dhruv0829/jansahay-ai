from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminUserAccessUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class AdminSchemeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=2, max_length=255)
    short_name: Optional[str] = Field(default=None, max_length=100)
    department: str = Field(min_length=2, max_length=255)
    ministry: Optional[str] = Field(default="Government of India", max_length=255)
    level: str = Field(default="Central", max_length=50)
    applicable_states: str = Field(default="All", max_length=500)
    category: str = Field(min_length=2, max_length=100)
    summary: str = Field(min_length=10)
    description: str = Field(min_length=10)
    target_beneficiary: Optional[str] = Field(default="Eligible Citizens", max_length=255)
    benefit_type: str = Field(min_length=2, max_length=100)
    benefit_amount: str = Field(min_length=2, max_length=255)
    application_mode: str = Field(default="Online", max_length=50)
    official_url: str = Field(min_length=8, max_length=500)
