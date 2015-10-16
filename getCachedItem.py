#!/usr/bin/python
##############################################################################
#
# getCachedItem.py - Version 0.4 , by MJKazin (mkazin@gmail.com)
#  Based on version 0.3 of the identically-named Perl script version
#
#  A simple caching mechanism for use when downloading web pages
#
# Requires:
#  * urllib2 used for webpage downloading
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
#  * v 0.3 -	Switched to urllib2, now sending User-Agent
#  * v 0.4 -	Created class to add functionality (maintaining backward compatability)
#		Setting user agent possible
#		Users can now query status
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

import urllib2, os, time

#VERBOSE = 0

# Number of seconds in a day.  We will multiply this by cacheTime which is provided in days.
DAYSTOSECONDS = 60 * 60 * 24

ERROR_MESSAGE = "Error in getCachedItem().  No cached or downloaded file."

STATUS_ERROR = -3
STATUS_NO_FILE_SET = -2
STATUS_EXPIRED = -1
STATUS_NOT_IN_CACHE = 0
STATUS_VALID = 1


class GetCachedItem(object):

	def __init__(self):
		self.useragent = 'getCachedItem/0.4'
		self.status = STATUS_NO_FILE_SET
		self.verbose = 0

	def getCachedItem(this, cacheTime, cacheName, sourceURL, extraHeaders=None):

		if this.verbose:
			print "gCI: Entered getCachedItem() with following params:"
			print "  cacheTime	: " + str(cacheTime)
			print "  cacheName	: " + cacheName
			print "  sourceURL	: " + sourceURL
  

		# Caching limit- delete cache if it is old 
		if this.verbose: print "Checking for expired cached item..."
		if os.path.exists(cacheName):
			cacheAge = time.time() - os.path.getmtime(cacheName) #time.gmtime() - os.path.getmtime(cacheName)
			if this.verbose: print "gCI: Found cache item (" + cacheName + ")",
			if this.verbose: print " its age is " + str(cacheAge) + " seconds"
			if  cacheAge > (cacheTime * DAYSTOSECONDS):
				if this.verbose: print "gCI:   Cached item is expired.  Deleting it."
				os.remove(cacheName)
			else:
				if this.verbose: print "gCI:   Cached item has NOT expired."
		else:
			if this.verbose: print "  gCI: No cached item found (" + cacheName + ")"


		if this.verbose: print "gCI: Re-Checking for existing (non-expired) cache item..."
		if not os.path.exists(cacheName):
	
			# Download the file and store it in the cache
			if this.verbose: print "  gCI: Downloading page for (" + sourceURL + ") , using USER AGENT: " + this.useragent + " ..."
	
			opener = urllib2.build_opener()
			opener.addheaders = [('User-Agent' , this.useragent )]
			if extraHeaders is not None:
				opener.addheaders = opener.addheaders + extraHeaders
			i = opener.open(sourceURL)
			o = open(cacheName, 'w')
	
			while 1:
				buf = i.read(2048)
				if not len(buf):
					break
				#sys.stdout.write(buf)

				o.write(buf)

			i.close()
			o.close()


		if this.verbose: print "gCI: Reading cached item for return..."
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


	def getCacheStatus(this, cacheTime, cacheName):

		if this.verbose: print "Checking for item in cache..."
		if os.path.exists(cacheName):

			cacheAge = time.time() - os.path.getmtime(cacheName) #time.gmtime() - os.path.getmtime(cacheName)
			if this.verbose: print "gCI: Found cache item (" + cacheName + ")",
			if this.verbose: print " its age is " + str(cacheAge) + " seconds"
			if  cacheAge > (cacheTime * DAYSTOSECONDS):
				return STATUS_EXPIRED
			else:
				return STATUS_VALID
		else:
			if this.verbose: print "gCI: Did not find item in cache (" + cacheName + ")",
			return STATUS_NOT_IN_CACHE
	
		if this.verbose: print "gCI: Error searching item in cache (" + cacheName + ")",
		return STATUS_ERROR


	def setVerbose(this, newState):
		this.verbose = newState

	def setUserAgent(this, newAgent):
		this.useragent = newAgent

	def getLastStatus(this):
		return this.status


# For backward-compatability, we're keeping a copy of non-classed functions.
def getCachedItem(cacheTime, cacheName, sourceURL):
	gci = GetCachedItem()
	return gci.getCachedItem(cacheTime, cacheName, sourceURL)

def getCacheStatus(cacheTime, cacheName):
	gci = GetCachedItem()
	return gci.getCacheStatus(cacheTime, cacheName)
