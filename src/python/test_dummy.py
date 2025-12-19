# tests/test_sample.py


def test_answer():
    assert (1 + 1) == 2


def test_fail():
    # This will fail, proving pytest is reporting correctly
    assert (1 + 1) != 3
