# -*- coding: utf-8 -*-
"""
threshold_controller.py — Quản lý ngưỡng (threshold) cho routing.
"""

from typing import List, Literal

class ThresholdController:
    def __init__(
        self, 
        mode: Literal["fixed", "adaptive"] = "fixed",
        threshold: float = 0.75
    ):
        self.mode = mode
        self.threshold = threshold

    def get_threshold(self, scores: List[float] = None) -> float:
        """
        Lấy ngưỡng hiện tại.
        Trong Phase 2/Baseline, dùng fixed threshold 0.75.
        Adaptive threshold sẽ được implement sau (ở Phase 5).
        """
        if self.mode == "fixed":
            return self.threshold
        elif self.mode == "adaptive":
            # TBD: Adaptive logic based on scores distribution
            return self.threshold
        return self.threshold
