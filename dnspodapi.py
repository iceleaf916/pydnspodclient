#!/usr/bin/env python
# coding=utf-8

# Released under GPLv3.
# Author : iceleaf916@gmail.com

import urllib
import urllib2
import json

class DnspodApi():
    def __init__ (self):
        global VERSION
        user_agent = 'PyDNSPodClient/' + VERSION + '(iceleaf916@gmail.com)'
        self.headers = { 'User-Agent' : user_agent }
        self.values = {'login_email' : USER_MAIL,
          'login_password' : PASSWORD,
          'format' : 'json' }

    def getAPIVer(self):
        data = urllib.urlencode(values)
        ver_req = urllib2.Request(api_ver_url, data, headers)
        response = urllib2.urlopen(ver_req)
        js = response.read()
        return json.loads(js)

    def getDomainList(self):
        temp_values = self.values.copy()
        temp_values['type'] = 'mine'
        temp_values['offset'] = '0'
        temp_values['length'] = '20'
        data = urllib.urlencode(temp_values)
        domain_list_req = urllib2.Request(domain_list_url, data, self.headers)
        response = urllib2.urlopen(domain_list_req)
        js = response.read()
        return json.loads(js)

if __name__ == "__main__":
    dnspod_api = DnspodApi()
    list_js = dnspod_api.getDomainList()
    print list_js.get("status").get("code")
