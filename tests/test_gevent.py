import pytest
from tkshapes.gevent import GEvent, GEventQueue

def test_event_queue_rejects_int():
    with pytest.raises(TypeError):
        q = GEventQueue('test_queue')
        q.put_event(1)

def test_event_queue_rejects_str():
    with pytest.raises(TypeError):
        q = GEventQueue('test_queue')
        q.put_event('foo')

def test_event_id_type():
    g_event_1 = GEvent('Test1', None)
    assert type(g_event_1.event_id) is int

def test_event_id_increment():
    g_event_1 = GEvent('Test1', None)
    g_event_2 = GEvent('Test2', None)
    assert g_event_1.event_id + 1 == g_event_2.event_id

def test_event_type():
    g_event_1 = GEvent('Test1', None)
    assert g_event_1.event_type == 'Test1'

def test_event_queue_name():
    q = GEventQueue('test_queue')
    q_name = q.name
    assert q_name == 'test_queue'

def test_event_queue_empty():
    q = GEventQueue('test_queue')
    assert q.is_empty() is True

def test_event_queue_not_empty():
    q = GEventQueue('test_queue')
    g_event_1 = GEvent('Test1', None)
    q.put_event(g_event_1)
    assert q.is_empty() is False

def test_event_queue_full():
    q = GEventQueue('test_queue', maxsize=1)
    g_event_1 = GEvent('Test1', None)
    q.put_event(g_event_1)
    assert q.is_full() is True

def test_event_queue_not_full():
    q = GEventQueue('test_queue', maxsize=2)
    g_event_1 = GEvent('Test1', None)
    q.put_event(g_event_1)
    assert q.is_full() is False

def test_get_on_empty_queue():
    q = GEventQueue('test_queue')
    assert q.get_event() is None

def test_put_on_full_queue():
    q = GEventQueue('test_queue', maxsize=2)
    g_event_1 = GEvent('Test1', None)
    g_event_2 = GEvent('Test2', None)
    g_event_3 = GEvent('Test3', None)
    g_event_4 = GEvent('Test4', None)
    g_event_5 = GEvent('Test5', None)
    g_event_6 = GEvent('Test6', None)
    assert q.put_event(g_event_1) is True
    assert q.put_event(g_event_2) is True
    assert q.put_event(g_event_3) is False
    assert q.put_event(g_event_4) is False
    assert q.put_event(g_event_5) is False
    q.get_event()
    assert q.put_event(g_event_6) is True

def test_event_queue_size_after_put():
    q = GEventQueue('test_queue')
    g_event_1 = GEvent('Test1', None)
    g_event_2 = GEvent('Test2', None)
    g_event_3 = GEvent('Test3', None)
    g_event_4 = GEvent('Test4', None)
    q.put_event(g_event_1)
    q.put_event(g_event_2)
    q.put_event(g_event_3)
    q.put_event(g_event_4)
    assert q.get_qsize() == 4

def test_event_queue_size_after_get():
    q = GEventQueue('test_queue')
    g_event_1 = GEvent('Test1', None)
    g_event_2 = GEvent('Test2', None)
    g_event_3 = GEvent('Test3', None)
    g_event_4 = GEvent('Test4', None)
    q.put_event(g_event_1)
    q.put_event(g_event_2)
    q.put_event(g_event_3)
    q.put_event(g_event_4)
    q.get_event()
    q.get_event()
    assert q.get_qsize() == 2

