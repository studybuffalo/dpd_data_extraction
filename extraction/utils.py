"""Utility and helper functions for the script."""
import requests


def setup_session(config, log, extra_headers=None):
    """Sets up a Requests session to download zip files.

        Args:
            config (ojb): a Config object.
            log (obj): a Log object.
            extra_headers(dict): a dictionary for additional headers.
    """
    log.debug('Creating Requests session.')

    default_headers = {
        'User-Agent': config.download.robots_user_agent,
        'From': config.download.robots_from,
    }
    session_headers = {**default_headers, **extra_headers}
    session = requests.Session()
    session.headers.update(session_headers)

    return session
