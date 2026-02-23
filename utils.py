from typing import List, Any

def filter_values(value_list: List[Any]) -> List[int | float | str | bool]:
    return list(filter(lambda x: type(x) in [int, float, str, bool], value_list))


def str_to_ll_type(s: str) -> int | float | bool | str:
    try:
        # return bool if string is "true" or "false"
        if s.lower() in ["true", "false"]:
            return s.lower() == "true"

        # try converting string to float
        num = float(s)
        if num.is_integer():
            return int(num)
        else:
            return num
    except ValueError:
        # If float conversion fails, return the original string
        return s


print(str_to_ll_type(""))