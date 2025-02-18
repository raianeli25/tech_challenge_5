import pytest

def fake_function():
    return "Hello world!!"

def test_fake_function():
    assert fake_function() == "Hello world!!"