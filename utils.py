from typing import List, Any

def filter_values(value_list: List[Any]) -> List[int | float | str | bool]:
    return list(filter(lambda x: type(x) in [int, float, str, bool], value_list))
