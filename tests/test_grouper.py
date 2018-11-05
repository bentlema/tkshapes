
from tkshapes.gobjects.gpythonlogo import grouper

def test_grouper_with_list():
    list1 = [1, 2, 3, 4]
    result = grouper(list1, 2)
    assert list(result) == [(1, 2), (3, 4)]

def test_grouper_with_4_tuple():
    tuple1 = (1, 2, 3, 4)
    result = grouper(tuple1, 2)
    assert list(result) == [(1, 2), (3, 4)]

