def check_is_type(obj, type_list):
    for type in type_list:
        if type in obj.type:
            return True
    return False
