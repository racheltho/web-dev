import unittest
from validation import (valid_username,
                        valid_password,
                        valid_email)


class TestValidation(unittest.TestCase):
    def test_valid_username(self):
        assert valid_username('rachel_thomas')

    def test_invalid_username(self):
        assert not valid_username('rachel thomas')
        assert not valid_username('rt')

    def test_valid_password(self):
        assert valid_password('1234')

    def test_invalid_password(self):
        assert not valid_password('12')

    def test_valid_email(self):
        assert valid_email('rt@gmail.com')

    def test_invalid_email(self):
        assert not valid_email('rachel.com')
        assert not valid_email('rachel@com')
