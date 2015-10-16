##############################################################################
#
# getAuthenticatedCachedItem.py - Version 0.2 , by Michael J. Kazin
#
# Subclass of getCachedItem, providing a HTTP authentication mechanism
#
# Notes:
#       Cache time is counted in days, or fractions thereof.  So...
#               1     = 1 day      ;    7      = 1 week
#               0.5   = 12 hours   ;    0.0417 ~ 1 hour
#
#  Changelog:
#  * v 0.1 -    Initial version
#  * v 0.2 -    Fixed cached token file expiration so we stop failing with
#               authtication errors due to using an expired token
#
##############################################################################

from getCachedItem import GetCachedItem
from getCachedItem import STATUS_VALID
import json
import os

DEBUG = False
TOKEN_CACHE_TIME = 1        # 1 day
AUTH_URL = 'http://pedalcoach.linkedrive.com/pdl/api/authenticate'

class PCAuthenticatedCachedItem:

    def __init__(self, username, password, token_file):
        '''
        @summary: Wrapper for GetCachedItem which adds the ability to perform authenticated calls to DATA
            To use this class, use the following sample code, modifying the respective values:
            - username, password, and token file
            - cache_time (decimal, in days), cached file, REST URL

            # Instantiate the access class:
            gaci = PCAuthenticatedCachedItem('data_user', 'clearTextPassword', 'my_token.json')

            # Perform a request against the REST API:
            response = gaci.getCachedItem(0.0000001, 'testPCAuthenticatedCachedItem.tmp', 'http://pedalcoach.linkedrive.com/pdl/api/driver/45')
        '''
        self.gci = GetCachedItem()
        self.gci.setUserAgent('PCAuthenticatedCachedItem/0.2')
        self.gci.setVerbose(0)

        self.username = username
        self.password = password
        self.token_file = token_file
        self.authentication_token = None

    def authenticate(self):
        '''
        @summary: DO NOT CALL MANUALLY.  Handles authentication with DATA
        @result: Returns nothing, only used to set internal values.
        '''
        # Check the token's age
        status = self.gci.getCacheStatus(TOKEN_CACHE_TIME, self.token_file)
        if status != STATUS_VALID:
            if DEBUG: print 'Token in cache is invalid.'
            # Cache is invalid, we'll delete the file to force re-authentication
            self.authentication_token = None
            try:
                os.remove(self.token_file)
            except OSError:
                pass

        if self.authentication_token is None:

            try:
                with open(self.token_file, 'r') as f:
                    content = f.readline()
                    auth_file = json.loads(content)
                    self.authentication_token = auth_file['token']
                    if DEBUG: print 'Token loaded from file'
            except IOError:
                # We don't have the file, log in to the website to get a token and generate one
                if DEBUG: print 'No token file found.  Logging into DATA'
                auth_headers = [('username', self.username), ('password', self.password)]
                response = json.loads(self.gci.getCachedItem(TOKEN_CACHE_TIME, self.token_file, AUTH_URL, auth_headers))
                if DEBUG: print 'Response = ' + str(response)
                self.authentication_token = response['token']
                # Stash it in the token file
                with open(self.token_file, 'w') as f:
                    f.write(json.dumps(response))

    def getCachedItem(self, cacheTime, cacheName, sourceURL):
        '''
        @summary: Authenticates with DATA and performs a query
        @param cacheTime: Time a query is stored in cache before it expires
        @param cacheName: Filename where the query is stored
        @param sourceURL: URL to query
        @result: whatever JSON/HTML is returned from the supplied URL
        '''
        token_header = None

        # Shortcut to avoid logging in if not necessary:
        #   We'll test the cache status to see if we can pull the item, so that the
        #   only time we authenticate is on cache misses
        status = self.gci.getCacheStatus(cacheTime, cacheName)
        if status != STATUS_VALID:
            if DEBUG: print 'Cache invalid.  Calling authenticate()'

            # Handle authentication- either from file-stored token, or get one from DATA
            self.authenticate()

            token_header = [('token', self.authentication_token)]

        return self.gci.getCachedItem(cacheTime, cacheName, sourceURL, token_header)
