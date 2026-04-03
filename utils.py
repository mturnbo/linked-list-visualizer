from typing import List, Any

def filter_values(value_list: List[Any]) -> List[int | float | str | bool]:
    return list(filter(lambda x: type(x) in [int, float, str, bool], value_list))


def to_ll_type(val: Any) -> int | float | bool | str:
    # return bool if value is string and equals "true" or "false"
    if isinstance(val, str) and val.lower() in ["true", "false"]:
        return val.lower() == "true"

    try:
        # try converting string to float
        num = float(val)
        if num.is_integer():
            return int(num)
        else:
            return num
    except ValueError:
        # If float conversion fails, return the original string
        return val
