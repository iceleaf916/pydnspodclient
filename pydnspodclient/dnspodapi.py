#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import json

INFO_VERSION_URL = "https://dnsapi.cn/Info.Version"

DOMAIN_LIST_URL = 'https://dnsapi.cn/Domain.List'
DOMAIN_CREATE_URL = 'https://dnsapi.cn/Domain.Create'
DOMAIN_REMOVE_URL = 'https://dnsapi.cn/Domain.Remove'
DOMAIN_STATUS_URL = 'https://dnsapi.cn/Domain.Status'

RECORD_LIST_URL = 'https://dnsapi.cn/Record.List'
RECORD_MODIFY_URL = 'https://dnsapi.cn/Record.Modify'
RECORD_CREATE_URL = 'https://dnsapi.cn/Record.Create'
RECORD_REMOVE_URL = 'https://dnsapi.cn/Record.Remove'
RECORD_STATUS_URL = 'https://dnsapi.cn/Record.Status'

class DnspodApi():
    def __init__ (self, user_mail, user_passwd, client_agent):
        
        self.headers = { 'User-Agent' : client_agent }
        self.values = {'login_email' : user_mail,
                       'login_password' : user_passwd,
                       'format' : 'json' }

    def getInfoVersion (self):
        temp_values = self.values.copy()
        data = urllib.urlencode(temp_values)
        info_version_req = urllib2.Request(INFO_VERSION_URL, data, self.headers)
        response = urllib2.urlopen(info_version_req)
        js = response.read()
        return json.loads(js)

    def getDomainList(self):
        temp_values = self.values.copy()
        temp_values['type'] = 'mine'
        temp_values['offset'] = '0'
        temp_values['length'] = '20'
        data = urllib.urlencode(temp_values)
        domain_list_req = urllib2.Request(DOMAIN_LIST_URL, data, self.headers)
        response = urllib2.urlopen(domain_list_req)
        js = response.read()
        return json.loads(js)

    def getRecordList(self, domain_id):
        temp_values = self.values.copy()
        temp_values['length'] = '30'
        temp_values['offset'] = '0'
        temp_values['domain_id'] = domain_id
        data = urllib.urlencode(temp_values)
        record_list_req = urllib2.Request(RECORD_LIST_URL, data, self.headers)
        response = urllib2.urlopen(record_list_req)
        js = response.read()
        return json.loads(js)

    def recordModify(self, domain_id, record_id, sub_domain, record_type, \
                     record_line, record_value, record_mx, record_ttl):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        temp_values['record_id'] = record_id
        temp_values['sub_domain'] = sub_domain
        temp_values['record_type'] = record_type
        temp_values['record_line'] = record_line
        temp_values['value'] = record_value
        temp_values['mx'] = record_mx
        temp_values['ttl'] = record_ttl
        data = urllib.urlencode(temp_values)
        record_mod_req = urllib2.Request(RECORD_MODIFY_URL, data, self.headers)
        response = urllib2.urlopen(record_mod_req)
        js = response.read()
        return json.loads(js)

    def recordRemove(self, domain_id, record_id):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        temp_values['record_id'] = record_id
        data = urllib.urlencode(temp_values)
        record_remove_req = urllib2.Request(RECORD_REMOVE_URL, data, self.headers)
        response = urllib2.urlopen(record_remove_req)
        js = response.read()
        return json.loads(js)

    def createRcord(self, domain_id, sub_domain, record_type, record_line, \
                    record_value, record_mx, record_ttl):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        temp_values['sub_domain'] = sub_domain
        temp_values['record_type'] = record_type
        temp_values['record_line'] = record_line
        temp_values['value'] = record_value
        temp_values['mx'] = record_mx
        temp_values['ttl'] = record_ttl
        data = urllib.urlencode(temp_values)
        record_cre_req = urllib2.Request(RECORD_CREATE_URL, data, self.headers)
        response = urllib2.urlopen(record_cre_req)
        js = response.read()
        return json.loads(js)
        
    def createDomain(self, domain):
        temp_values = self.values.copy()
        temp_values['domain'] = domain
        data = urllib.urlencode(temp_values)
        domain_cre_req = urllib2.Request(DOMAIN_CREATE_URL, data, self.headers)
        js = urllib2.urlopen(domain_cre_req).read()
        return json.loads(js)

    def removeDomain(self, domain_id):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        data = urllib.urlencode(temp_values)
        domain_remove_req = urllib2.Request(DOMAIN_REMOVE_URL, data, self.headers)
        js = urllib2.urlopen(domain_remove_req).read()
        return json.loads(js)