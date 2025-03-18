import pytest
from touche_rad.core import create_strategy
from touche_rad.core.strategy.drivers.random import RandomStrategy
from touche_rad.core.strategy.drivers.always_attack import AlwaysAttackStrategy
from touche_rad.core.strategy.drivers.always_defend import AlwaysDefendStrategy


# we only need to test a subset of strategies here
@pytest.mark.parametrize(
    "name, cls",
    [
        ("random", RandomStrategy),
        ("always_attack", AlwaysAttackStrategy),
        ("always_defend", AlwaysDefendStrategy),
    ],
)
def test_create_strategy_valid(name, cls):
    strategy = create_strategy(name)
    assert isinstance(strategy, cls)


def test_create_strategy_invalid():
    with pytest.raises(ValueError):
        create_strategy("nonexistent")
