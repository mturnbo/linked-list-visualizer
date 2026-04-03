from utils import filter_values,  to_ll_type


def test_filter_values():
    not_valid = object()
    assert filter_values([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert filter_values([not_valid, 2, 3, 4]) == [2, 3, 4]
    assert filter_values(["a", "b", "c"]) == ["a", "b", "c"]

    assert filter_values([True, False]) == [True, False]
    assert filter_values([True, False, not_valid]) == [True, False]


def test_to_ll_type_conversion():
    assert to_ll_type("123") == 123
    assert to_ll_type("123.456") == 123.456
    assert to_ll_type("true") is True
    assert to_ll_type("false") is False
    assert to_ll_type("abc") == "abc"