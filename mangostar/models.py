from datetime import datetime
from typing import Any, Dict, Union

from mangostar.core import FlexibleModel


class Measurement(FlexibleModel):
    tags: Dict[str, Any] = {}
    clock_at: datetime
    created_at: datetime = datetime.now()
    subject: str
    value: str
    dtype: str

    def processed(self):
        resp = self.dict()
        resp.update(self.timestamp_dt())
        return resp

    def timestamp_dt(self):
        return {
            "clock_at": self.clock_at.timestamp(),
            "created_at": self.created_at.timestamp(),
        }


class MeasureSet(FlexibleModel):
    tags: Dict[str, Any] = {}
    clock_at: datetime
    created_at: datetime = datetime.now()
    subject: str
    values: Dict[str, Any] = {}

    def get_insertable(self):
        """Return a list of insertable values. To insert values in a batch."""
        measures_with_timestamps = []
        if not self.values:
            raise ValueError("Values cannot be empty")
        for name, val in self.values.items():
            measure = Measurement(
                name=name,
                value=val,
                tags=self.tags,
                dtype=type(val).__name__,
                subject=self.subject,
                clock_at=self.clock_at,
                created_at=self.created_at,
            )
            measures_with_timestamps.append(measure.processed())
        return measures_with_timestamps
