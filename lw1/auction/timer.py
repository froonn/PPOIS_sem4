from typing import Callable, Any

import threading


class Timer:
    """
    A class for managing a timer that executes a callback after a specified timeout.

    Args:
        timeout (float): The timeout in seconds before the callback is executed.
        callback (Callable[..., Any]): The function to call when the timer expires.
    """

    def __init__(self, timeout: float, callback: Callable[..., Any]):
        """
        Initializes the Timer with a timeout and a callback function.

        Args:
            timeout (float): The timeout in seconds.
            callback (Callable[..., Any]): The function to call when the timer expires.
        """
        self._timer = None
        self._timeout = timeout
        self._callback = callback

    def __repr__(self):
        """
        Returns a string representation of the Timer.

        Returns:
            str: A string representation of the Timer.
        """
        return f"Timer(timeout={self._timeout}, callback={self._callback})"

    def start(self):
        """
        Starts the timer. If a timer is already running, it is canceled first.
        """
        if self._timer:
            self._timer.cancel()
        self._timer = threading.Timer(self._timeout, self._callback)
        self._timer.start()

    def cancel(self):
        """
        Cancels the timer if it is running.
        """
        if self._timer:
            self._timer.cancel()
            self._timer = None
