from .drivers.base import BaseStrategy


def create_strategy(name: str, *args, **kwargs) -> BaseStrategy:
    """Factory function that creates and returns a strategy instance based on the provided name.

    Args:
        name: The name of the strategy to create (snake_case, without the "_strategy" suffix)
        *args: Positional arguments to pass to the strategy constructor
        **kwargs: Keyword arguments to pass to the strategy constructor

    Returns:
        An instance of the specified strategy

    Raises:
        ValueError: If the specified strategy does not exist
    """
    for cls in BaseStrategy.__subclasses__():
        if cls.name == name:
            return cls(*args, **kwargs)
    raise ValueError(f"Strategy '{name}' does not exist.")
