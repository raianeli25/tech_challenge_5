import pytest

def fake_function():
    return "Hello, Pytest!"

def test_fake_function():
    assert fake_function() == "Hello, Pytest!"