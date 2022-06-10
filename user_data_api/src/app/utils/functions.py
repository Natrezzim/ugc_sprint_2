"""App utils."""


def get_rating(like_by, dislike_by) -> float:
    if not like_by:
        return 0.0
    return len(like_by) * 10 / (len(like_by) + len(dislike_by))