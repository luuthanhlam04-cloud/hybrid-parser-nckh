import random

EVAL_SOFT_LIMIT_USD = 5.0
EVAL_HARD_LIMIT_USD = 10.0

def set_global_seed(seed: int = 42):
    """
    Cố định Random Seed để đảm bảo tính Deterministic (có thể tái tạo kết quả).
    Bắt buộc phải gọi trong các class Hệ thống Baseline.
    """
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
