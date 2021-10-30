"""
test_mkname
~~~~~~~~~~~
"""
import unittest as ut
from typing import Mapping

from mkname import mkname as mn


# Test cases.
class InitializationTestCase(ut.TestCase):
    def assertConfigEqual(self, a: Mapping, b: Mapping) -> None:
        """Assert that two ParserConfig objects are equal."""
        a_keylist = list(a.keys())
        b_keylist = list(b.keys())
        self.assertListEqual(a_keylist, b_keylist)
        for key in a:
            if not isinstance(a[key], str):
                self.assertConfigEqual(a[key], b[key])
            else:
                self.assertEqual(a[key], b[key])

    def test_load_config(self):
        """When called, load_config() should return a mapping that
        contains the mkname configuration from the given configuration
        file.
        """
        # Expected value.
        exp = {
            'db_path': 'spam.db',
        }

        # Test data and state.
        config_path = 'tests/data/test_load_config.conf'

        # Run test.
        act = mn.load_config(config_path)

        # Determine test result.
        self.assertConfigEqual(exp, act)
