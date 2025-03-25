import functools

STATE_FILE = 'auction_state.json'  # File to save and load state

def ensure_state(*required_state):
    """
    Decorator to ensure a method executes only in a specific state.

    Args:
        *required_state: The states in which the method or property getter is allowed to execute.

    Returns:
        Callable: The decorated function or wrapped getter for properties.
    """

    def decorator(func):
        if isinstance(func, property):
            # Handle property getter - simply wrap and return getter's result
            fget = func.fget
            if fget is None:
                raise ValueError("Cannot apply ensure_state to a property without a getter.")

            @functools.wraps(fget)
            def wrapper_getter(self):
                if self.state not in required_state:
                    raise RuntimeError(
                        f"Cannot access property '{func.fget.__name__}' in state '{self.state}' "
                        f"(requires {' OR '.join(required_state)})"
                    )
                return fget(self)  # Return result of getter, not a property object

            return wrapper_getter  # Return wrapped getter function

        else:
            # Handle regular method - as before
            @functools.wraps(func)
            def wrapper_method(self, *args, **kwargs):
                if self.state not in required_state:
                    raise RuntimeError(
                        f"Cannot execute {func.__name__} in state '{self.state}' "
                        f"(requires {' OR '.join(required_state)})"
                    )
                return func(self, *args, **kwargs)

            return wrapper_method

    return decorator


def save(func):
    """
    Decorator to save state after the decorated function execution.
    This decorator works for methods as before. No changes needed for property setters if you intend to use it there.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._save_state()
        return result

    return wrapper
