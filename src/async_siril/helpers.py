from __future__ import annotations

import pathlib
import typing as t
import structlog.stdlib

from dataclasses import dataclass
from async_siril.command_types import stack_rejection

log = structlog.stdlib.get_logger()


@dataclass
class BestRejection:
    method: stack_rejection
    low_threshold: float
    high_threshold: float

    @staticmethod
    def find_best_rejection(images: t.List[pathlib.Path]) -> BestRejection:
        if len(images) == 0:
            raise ValueError("At least 1 image is required to find the best rejection")
        
        if len(images) <= 6:
            return BestRejection(
                method=stack_rejection.REJECTION_PERCENTILE,
                low_threshold=0.2,
                high_threshold=0.1,
            )
        elif 6 < len(images) <= 30:
            return BestRejection(
                method=stack_rejection.REJECTION_WINSORIZED,
                low_threshold=3,
                high_threshold=3,
            )
        else:
            return BestRejection(
                method=stack_rejection.REJECTION_LINEAR_FIT,
                low_threshold=5,
                high_threshold=5,
            )
            
        