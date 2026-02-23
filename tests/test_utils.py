from utils import filter_values,  str_to_ll_type


def test_filter_values():
    not_valid = object()
    assert filter_values([1, 2, 3, 4]) == [1, 2, 3, 4]
    assert filter_values([not_valid, 2, 3, 4]) == [2, 3, 4]
    assert filter_values(["a", "b", "c"]) == ["a", "b", "c"]

    assert filter_values([True, False]) == [True, False]
    assert filter_values([True, False, not_valid]) == [True, False]


def test_str_to_ll_type_conversion():
    assert str_to_ll_type("123") == 123
    assert str_to_ll_type("123.456") == 123.456
    assert str_to_ll_type("true") is True
    assert str_to_ll_type("false") is False
    assert str_to_ll_type("abc") == "abc"