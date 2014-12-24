import os


def is_development_env():
    try:
        return os.environ['SERVER_SOFTWARE'].startswith('Development')
    except KeyError:
        pass
