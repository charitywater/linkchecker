# -*- coding: iso-8859-1 -*-
# Copyright (C) 2004-2005  Bastian Kleineidam
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Test http checking.
"""

import unittest
import os
import re

import linkcheck.ftests.httptest


class TestHttp (linkcheck.ftests.httptest.HttpServerTest):
    """
    Test http:// link checking.
    """

    def test_html (self):
        self.start_server(handler=RedirectHttpRequestHandler)
        try:
            url = u"http://localhost:%d/linkcheck/ftests/data/http.html" % \
                  self.port
            resultlines = self.get_resultlines("http.html")
            self.direct(url, resultlines, recursionlevel=1)
            self.redirect_test()
            self.noproxyfor_test()
        finally:
            self.stop_server()

    def redirect_test (self):
        url = u"http://localhost:%d/redirect1" % self.port
        nurl = url
        rurl = url.replace("redirect", "newurl")
        resultlines = [
            u"url %s" % url,
            u"cache key %s" % nurl,
            u"real url %s" % rurl,
            u"info Redirected to %s." % rurl,
            u"error",
        ]
        self.direct(url, resultlines, recursionlevel=0)
        url = u"http://localhost:%d/linkcheck/ftests/data/redirect.html" % \
              self.port
        nurl = url
        rurl = url.replace("redirect", "newurl")
        resultlines = [
            u"url %s" % url,
            u"cache key %s" % nurl,
            u"real url %s" % rurl,
            u"info Redirected to %s." % rurl,
            u"valid",
            u"url newurl.html (cached)",
            u"cache key %s" % nurl.replace("redirect", "newurl"),
            u"real url %s" % rurl.replace("redirect", "newurl"),
            u"name Recursive Redirect",
            u"info Redirected to %s." % rurl,
            u"valid",
        ]
        self.direct(url, resultlines, recursionlevel=99)

    def noproxyfor_test (self):
        """
        Test setting proxy and --no-proxy-for option.
        """
        os.environ["http_proxy"] = "http://imadoofus:8877"
        confargs = {"noproxyfor": [re.compile("localhost")]}
        url = u"http://localhost:%d/linkcheck/ftests/data/http.html" % \
              self.port
        nurl = url
        resultlines = [
            u"url %s" % url,
            u"cache key %s" % nurl,
            u"real url %s" % nurl,
            u"info Ignoring proxy setting 'imadoofus:8877'",
            u"valid",
        ]
        self.direct(url, resultlines, recursionlevel=0,
                    confargs=confargs)
        del os.environ["http_proxy"]


class RedirectHttpRequestHandler (linkcheck.ftests.httptest.NoQueryHttpRequestHandler):
    """
    Handler redirecting certain requests.
    """

    def redirect (self):
        """
        Redirect request.
        """
        path = self.path.replace("redirect", "newurl")
        self.send_response(302)
        self.send_header("Location", path)
        self.end_headers()

    def do_GET (self):
        """
        Removes query part of GET request.
        """
        if "redirect" in self.path:
            self.redirect()
        else:
            super(RedirectHttpRequestHandler, self).do_GET()

    def do_HEAD (self):
        if "redirect" in self.path:
            self.redirect()
        else:
            super(RedirectHttpRequestHandler, self).do_HEAD()


def test_suite ():
    """
    Build and return a TestSuite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHttp))
    return suite


if __name__ == '__main__':
    unittest.main()
