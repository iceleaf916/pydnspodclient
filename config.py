#!/usr/bin/env python
# -*- coding: utf-8 -*-

USER_MAIL = ''
PASSWORD = ''

VERSION = "1.0.0"

# dnspod api request urls

domain_list_url = 'https://dnsapi.cn/Domain.List'
domain_cre_url = 'https://dnsapi.cn/Domain.Create'
domain_remove_url = 'https://dnsapi.cn/Domain.Remove'
domain_status_url = 'https://dnsapi.cn/Domain.Status'

record_list_url = 'https://dnsapi.cn/Record.List'
record_mod_url = 'https://dnsapi.cn/Record.Modify'
record_cre_url = 'https://dnsapi.cn/Record.Create'
record_remove_url = 'https://dnsapi.cn/Record.Remove'
record_status_url = 'https://dnsapi.cn/Record.Status'

record_types = ["A", "CNAME", "MX", "URL", "NS", "TXT", "AAAA"]
record_lines = ["默认", "电信", "联通", "教育网"]

domain_id_dict = {}

key = 'abcdefghijklmnop' # u can change this key(must be 16 bytes)
