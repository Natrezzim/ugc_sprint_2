"""App utils."""
from typing import List


def get_rating(like_by: List[str], dislike_by: List[str]) -> float:
    if not like_by:
        return 0.0
    return len(like_by) * 10 / (len(like_by) + len(dislike_by))
