#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

VERSION = "1.2.1"
CLIENT_AGENT = "PyDNSPod Client/"+VERSION+" (iceleaf916@gmail.com)"

CURRENT_DIR = os.path.dirname(__file__)
GLADE_FILE = os.path.join(CURRENT_DIR, "main.glade")
LOGO_FILE = os.path.join(CURRENT_DIR, "dnspod.png")

RECORD_TYPES = ["A", "CNAME", "MX", "URL", "NS", "TXT", "AAAA"]
RECORD_LINES = ["默认", "电信", "联通", "教育网"]

domain_id_dict = {}

key = 'abcdefghijklmnop' # u can change this key(must be 16 bytes)

license = '''\
This program is a free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA.
'''

if __name__ == "__main__":
    print CLIENT_AGENT
