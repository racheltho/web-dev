import random
import string
import hashlib
import hmac
from secret import SECRET


# functions for hashing cookies
def hash_str(s):
    return hmac.new(SECRET, str(s)).hexdigest()
    

def make_secure_val(s):
    return '|'.join([str(s), hash_str(s)])


def check_secure_val(h):
    # take a string of the format s,HASH
    # and returns s if hash_str(s) == HASH, otherwise None
    s, HASH = h.split('|')
    if hash_str(s) == HASH:
        return s


# functions for hashing passwords
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '|'.join([h, salt])


def valid_pw(name, pw, h):
    salt = h.split('|')[1]
    if h == make_pw_hash(name, pw, salt):
        return True
