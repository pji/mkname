"""
test_roll
~~~~~~~~~

Unit tests for mkname.roll.
"""
import unittest as ut

from mkname import dice as r


# Test cases.
@ut.skip
class RollTestCase(ut.TestCase):
    def test_roll(self):
        """Given a dice code as a string, return a randomly generated
        number within the range of the dice code.
        """
        # Expected value.
        exp = 2

        # Test data and state.
        r.seed('spam')
        code = '1d10'

        # Run test.
        act = r.roll(code)

        # Determine test result.
        self.assertEqual(exp, act)

    def test_roll_plus_one(self):
        """Given a dice code as a string, return a randomly generated
        number within the range of the dice code.
        """
        # Expected value.
        exp = 3

        # Test data and state.
        r.seed('spam')
        code = '1d10+1'

        # Run test.
        act = r.roll(code)

        # Determine test result.
        self.assertEqual(exp, act)
