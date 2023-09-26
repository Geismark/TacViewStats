def str_is_float(string: str) -> bool:
    """Returns bools of whether string is a float-able or not."""
    try:
        float(string)
        return True
    except ValueError:
        return False
