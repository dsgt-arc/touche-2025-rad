from touche_rad.spark import get_spark


def test_get_spark():
    assert get_spark() is not None
