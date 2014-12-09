import unittest
from hashing import (hash_str,
                     make_secure_val,
                     check_secure_val,
                     make_salt,
                     make_pw_hash,
                     valid_pw)
from secret import SECRET


class TestHashing(unittest.TestCase):
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

