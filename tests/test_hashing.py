import unittest
from google.appengine.ext import testbed

from hashing import (hash_str,
                     make_secure_val,
                     check_secure_val,
                     generate_reset,
                     make_pw_hash,
                     valid_pw)
from models import ResetToken


class TestHashing(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def teardown(self):
        self.testbed.deactivate()

    def test_hash_str(self):
        HASH = "cea6b92de1c15cfdbcf333982d340d3f"
        assert hash_str("test") == HASH

    def test_make_secure_val(self):
        h = "test|cea6b92de1c15cfdbcf333982d340d3f"
        assert make_secure_val("test") == h

    def test_check_secure_val(self):
        h = "test|cea6b92de1c15cfdbcf333982d340d3f"
        assert check_secure_val(h) == "test"

    def test_make_pw_hash(self):
        h = ("7772c62d210343d859a0c536c92845e72a443e22"
             "c378eb2132f1d925b71122e7|salt5")
        assert make_pw_hash("name", "password", "salt5") == h

    def test_valid_pw(self):
        h = ("7772c62d210343d859a0c536c92845e72a443e22"
             "c378eb2132f1d925b71122e7|salt5")
        assert valid_pw("name", "password", h)

    def test_generate_reset(self):
        reset_hash = generate_reset("test_user")
        reset_token = ResetToken.all().filter('username = ', 'test_user').get()
        assert reset_token.username == "test_user"
        assert reset_token.active
        assert reset_token.name_time_hash == reset_hash
