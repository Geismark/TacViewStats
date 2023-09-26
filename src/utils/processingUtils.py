def check_is_type(obj, type_list):
    """If obj.type shares element with type_list, returns True, else returns False."""
    for type in type_list:
        if type in obj.type:
            return True
    return False


def check_lists_share_element(list1: list, list2: list) -> bool:
    """Returns bools of whether list1 and list2 share element with each other."""
    # https://stackoverflow.com/a/17735466
    return not set(list1).isdisjoint(list2)


if __name__ == "__main__":
    a = [1, 2, 3]
    b = [4, 5, 6]
    print(check_lists_share_element(a, b))
