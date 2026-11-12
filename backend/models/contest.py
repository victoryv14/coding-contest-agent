from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Contest(BaseModel):
    """
    Canonical Contest Model.
    
    Standardized schema for contests across all competitive platforms
    (Codeforces, LeetCode, CodeChef).
    """
    id: str = Field(description="Globally unique contest identifier, e.g. 'cf-1950'")
    title: str = Field(description="Display title of the contest")
    platform: str = Field(description="Source platform: 'codeforces', 'leetcode', or 'codechef'")
    url: str = Field(description="Direct link to the contest page")
    start_time: datetime = Field(description="Contest start time (must be timezone-aware UTC)")
    end_time: datetime = Field(description="Contest end time (must be timezone-aware UTC)")
    duration_seconds: int = Field(description="Total duration in seconds")
    division: Optional[str] = Field(default=None, description="Category or division (e.g., 'Div. 2', 'Weekly')")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
