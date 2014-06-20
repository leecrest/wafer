# coding=utf-8
"""
@author : leecrest
@time   : 2014/6/19 22:33
@brief  : 
"""

from twisted.web.server import Request,Site
from twisted.internet import defer
from twisted.web import http,html
from twisted.python import reflect
from twisted.web import resource
from twisted.web.error import UnsupportedMethod
from twisted.web.microdom import escape
from wafer.utils import log

import string
import types

NOT_DONE_YET = 1

# backwards compatability
date_time_string = http.datetimeToString
string_date_time = http.stringToDatetime

#当前支持的方法
SUPPORT_METHOD_LIST = ("GET", "HEAD", "POST")


class CDelayRequest(Request):

	def __init__(self, *args, **kw):
		Request.__init__(self, *args, **kw)


	#渲染，继承自Request
	def render(self, resrc):
		"""
		Ask a resource to render itself.

		@param resrc: a L{twisted.web.resource.IResource}.
		"""
		try:
			body = resrc.render(self)
		except UnsupportedMethod, e:
			sAllowedMethodList = e.allowedMethods
			if (self.method == "HEAD") and ("GET" in sAllowedMethodList):
				# We must support HEAD (RFC 2616, 5.1.1).  If the
				# resource doesn't, fake it by giving the resource
				# a 'GET' request and then return only the headers,
				# not the body.
				log.Info("Using GET to fake a HEAD request for %s" % resrc)
				self.method = "GET"         #来自http.Request
				self._inFakeHead = True     #来自web.server.Request
				body = resrc.render(self)

				if body is NOT_DONE_YET:
					log.Info("Tried to fake a HEAD request for %s, but it got away from me." % resrc)
					# Oh well, I guess we won't include the content length.
				else:
					self.setHeader("content-length", str(len(body)))

				self._inFakeHead = False
				self.method = "HEAD"
				self.write("")
				self.finish()
				return

			if self.method in SUPPORT_METHOD_LIST:
				# We MUST include an Allow header
				# (RFC 2616, 10.4.6 and 14.7)
				self.setHeader('Allow', ', '.join(sAllowedMethodList))
				s = ("""Your browser approached me (at %(URI)s) with"""
					 """ the method "%(method)s".  I only allow"""
					 """ the method%(plural)s %(allowed)s here.""" % {
					"URI" : escape(self.uri),
					"method" : self.method,
					"plural" : ((len(sAllowedMethodList) > 1) and "s") or "",
					"allowed" : string.join(sAllowedMethodList, ", ")
					})
				epage = resource.ErrorPage(http.NOT_ALLOWED, "Method Not Allowed", s)
				body = epage.render(self)
			else:
				epage = resource.ErrorPage(
					http.NOT_IMPLEMENTED, "Huh?",
					"I don't know how to treat a %s request." %
					(escape(self.method),))
				body = epage.render(self)
		# end except UnsupportedMethod

		if body == NOT_DONE_YET:
			return
		if not isinstance(body, defer.Deferred) and type(body) is not types.StringType:
			body = resource.ErrorPage(
				http.INTERNAL_SERVER_ERROR,
				"Request did not return a string",
				"Request: " + html.PRE(reflect.safe_repr(self)) + "<br />" +
				"Resource: " + html.PRE(reflect.safe_repr(resrc)) + "<br />" +
				"Value: " + html.PRE(reflect.safe_repr(body))).render(self)

		if self.method == "HEAD":
			if len(body) > 0:
				# This is a Bad Thing (RFC 2616, 9.4)
				log.Info("Warning: HEAD request %s for resource %s is"
						" returning a message body."
						"  I think I'll eat it."
						% (self, resrc))
				self.setHeader("content-length", str(len(body)))
			self.write("")
			self.finish()
		else:
			if isinstance(body, defer.Deferred):
				body.addCallback(self.DeferWrite)
			else:
				self.setHeader("content-length", str(len(body)))
				self.write(body)
				self.finish()


	def DeferWrite(self, data):
		"""延迟等待数据返回
		"""
		self.setHeader("content-length", str(len(data)))
		self.write(data)
		self.finish()



class CDelaySite(Site):

	def __init__(self, resource, logPath=None, timeout=60*60*12):
		Site.__init__(self, resource, logPath=logPath, timeout=timeout)
		self.requestFactory = CDelayRequest


class CWebSite(resource.Resource):
	pass



__all__ = ["CDelaySite", "CResourceSite"]