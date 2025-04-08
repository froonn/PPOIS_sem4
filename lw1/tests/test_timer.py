import unittest
from unittest.mock import Mock
from auction import Timer

class TestTimer(unittest.TestCase):

    def test_timer_executes_callback_after_timeout(self):
        callback = Mock()
        timer = Timer(0.1, callback)
        timer.start()
        timer._timer.join()  # Wait for the timer to finish
        callback.assert_called_once()

    def test_timer_resets_if_started_again(self):
        callback = Mock()
        timer = Timer(0.1, callback)
        timer.start()
        timer.start()  # Restart the timer
        timer._timer.join()  # Wait for the timer to finish
        callback.assert_called_once()

    def test_timer_repr_returns_correct_string(self):
        callback = Mock()
        timer = Timer(0.1, callback)
        self.assertEqual(repr(timer), f"Timer(timeout=0.1, callback={callback})")

if __name__ == '__main__':
    unittest.main()