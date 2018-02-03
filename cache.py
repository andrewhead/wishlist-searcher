# /usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals
import logging
import time
import sys
import requests_cache


logging.basicConfig(level=logging.INFO, format="%(message)s")
CACHE_NAME = 'cache'
IS_PY2APP = hasattr(sys, "frozen")
PEM_PATH = "lib/python2.7/certifi/cacert.pem" if IS_PY2APP else None

requests_cache.install_cache(CACHE_NAME)
session = requests_cache.CachedSession(expire_after=60*60, verify=PEM_PATH)


def throttle_hook(timeout=1.0):
    '''
    Hook for throttling requests if not in cache.
    Snippet from
    http://requests-cache.readthedocs.org/en/latest/user_guide.html#usage.
    '''
    def hook(response, *args, **kwargs):
        if not getattr(response, 'from_cache', False):
            print "Pulling anew: caching"
            time.sleep(timeout)
        else:
            print "Found cached file, not sleeping."
        return response
    return hook


def get_session(timeout=1.0):
    session.hooks = {'response': throttle_hook(timeout)}
    return session
