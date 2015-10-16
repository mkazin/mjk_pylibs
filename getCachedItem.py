#!/usr/bin/python
##############################################################################
#
# getCachedItem.py - Version 0.2 , by MJKazin (mkazin@gmail.com)
#  Based on version 0.3 of the identically-named Perl script version
#
#  A simple caching mechanism for use when downloading web pages
#
# Requires:
#  * urllib used for webpage downloading
#  * os for dating and deleting cached files
#
# Notes:
# 	Cache time is counted in days, or fractions thereof.  So...
# 		1     = 1 day	   ;	7      = 1 week
# 		0.5   = 12 hours   ;	0.0417 ~ 1 hour
#
#  Changelog:
#  * v 0.1 -	Initial version, full port from the Perl (v 0.3).
#  * v 0.2 -	Added getCacheStatus() to allow callers to peek at the cache.
#
##############################################################################
#
# getCachedItem() - main function providing the download and caching
#
# Usage:
# 	filecontents = getCachedItem(cacheTime, cacheName, sourceURL)
#
# Inputs:
# 	Cache time   - how long before they cached item may be re-downloaded (see notes below)
#	Cache item   - filename under which the URL is to be stored (can include path)
#	Cache source - URL to download if the cache doesn't exist or hasn't expired
#
# Returns:
# 	The content of the file or ERROR_MESSAGE
#
##############################################################################

import urllib, os, time

VERBOSE = 0

# Number of seconds in a day.  We will multiply this by cacheTime which is provided in days.
DAYSTOSECONDS = 60 * 60 * 24

ERROR_MESSAGE = "Error in getCachedItem().  No cached or downloaded file."

STATUS_ERROR = -2
STATUS_EXPIRED = -1
STATUS_NOT_IN_CACHE = 0
STATUS_VALID = 1


def getCachedItem(cacheTime, cacheName, sourceURL):

	if VERBOSE:
		print "gCI: Entered getCachedItem() with following params:"
		print "  cacheTime	: " + str(cacheTime)
		print "  cacheName	: " + cacheName
		print "  sourceURL	: " + sourceURL
  

	# Caching limit- delete cache if it is old 
	if VERBOSE: print "Checking for expired cached item..."
	if os.path.exists(cacheName):
		cacheAge = time.time() - os.path.getmtime(cacheName) #time.gmtime() - os.path.getmtime(cacheName)
		if VERBOSE: print "gCI: Found cache item (" + cacheName + ")",
		if VERBOSE: print " its age is " + str(cacheAge) + " seconds"
		if  cacheAge > (cacheTime * DAYSTOSECONDS):
			if VERBOSE: print "gCI:   Cached item is expired.  Deleting it."
			os.remove(cacheName)
		else:
			if VERBOSE: print "gCI:   Cached item has NOT expired."
	else:
		if VERBOSE: print "  gCI: No cached item found (" + cacheName + ")"


	if VERBOSE: print "gCI: Re-Checking for existing (non-expired) cache item..."
	if not os.path.exists(cacheName):

		# Download the file and store it in the cache
		if VERBOSE: print "  gCI: Downloading page for (" + sourceURL + ")..."

		i = urllib.urlopen(sourceURL)
		o = open(cacheName, 'w')

		while 1:
			buf = i.read(2048)
			if not len(buf):
				break
			#sys.stdout.write(buf)

			o.write(buf)

		i.close()
		o.close()


	if VERBOSE: print "gCI: Reading cached item for return..."
	if os.path.exists(cacheName):
		i = open(cacheName, 'r')
		res = i.read()
		return res

	
	return ERROR_MESSAGE

##############################################################################
#
# getCacheStatus() - allows peekig at the cache without downloading
#
# Usage:
# 	status_code = getCacheStatus(cacheTime, cacheName)
#
# Inputs:
# 	Cache time   - how long before they cached item may be re-downloaded (see notes below)
#	Cache item   - filename under which the URL is to be stored (can include path)
#
# Returns:  
# 	One of the three status values: STATUS_VALID, STATUS_NOT_IN_CACHE, STATUS_EXPIRED
#  or STATUS_ERROR if something bad happens.
#
##############################################################################


def getCacheStatus(cacheTime, cacheName):

	if VERBOSE: print "Checking for item in cache..."
	if os.path.exists(cacheName):

		cacheAge = time.time() - os.path.getmtime(cacheName) #time.gmtime() - os.path.getmtime(cacheName)
		if VERBOSE: print "gCI: Found cache item (" + cacheName + ")",
		if VERBOSE: print " its age is " + str(cacheAge) + " seconds"
		if  cacheAge > (cacheTime * DAYSTOSECONDS):
			return STATUS_EXPIRED
		else:
			return STATUS_VALID
	else:
		return STATUS_NOT_IN_CACHE

	return STATUS_ERROR

