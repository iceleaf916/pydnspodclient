#!/usr/bin/env python
# coding=utf-8

# PyDNSPodClient version 0.2.0 for DNSPod API 2.8
# Released under GPLv3.
# Author : iceleaf916@gmail.com

import gtk
import urllib
import urllib2
import json

user = "kaisheng.ye@gmail.com"
password = "4262500yks"

values = {'login_email' : user,
          'login_password' : password,
          'format' : 'json' }

user_agent = 'PyDNSPodClient/0.0.1(iceleaf916@gmail.com)'
headers = { 'User-Agent' : user_agent }

# request urls
api_ver_url = 'https://dnsapi.cn/Info.Version'
user_info_url = 'https://dnsapi.cn/User.Info'
domain_list_url = 'https://dnsapi.cn/Domain.List'
domain_info_url = 'https://dnsapi.cn/Domain.Info'
record_type_url = 'https://dnsapi.cn/Record.Type'
record_line_url = 'https://dnsapi.cn/Record.Line'
record_list_url = 'https://dnsapi.cn/Record.List'
record_mod_url = 'https://dnsapi.cn/Record.Modify'
record_cre_url = 'https://dnsapi.cn/Record.Create'

domain_list = []

def getAPIVer():
    data = urllib.urlencode(values)
    ver_req = urllib2.Request(api_ver_url, data, headers)
    response = urllib2.urlopen(ver_req)
    js = response.read()
    return json.loads(js)

def getDomainList():
    temp_values = values.copy()
    temp_values['type'] = 'mine'
    temp_values['offset'] = '0'
    temp_values['length'] = '20'
    data = urllib.urlencode(temp_values)
    domain_list_req = urllib2.Request(domain_list_url, data, headers)
    response = urllib2.urlopen(domain_list_req)
    js = response.read()
    return json.loads(js)

def init_domain_list():
    list_js = getDomainList()
    if list_js.get("status").get("code") == "1":
        for y in list_js.get("domains"):
            a = (y.get("name"), y.get("grade"), y.get("status"), int(y.get("records")), y.get("id"))
            domain_list.append(a)
        return 1
    else:
        return list_js.get("status").get("code")

class PyApp(gtk.Window):
    def __init__(self):
        super(PyApp, self).__init__()
        
        self.set_size_request(680, 450)
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.connect("destroy", gtk.main_quit)
        self.set_title("ListView")

        vbox = gtk.VBox(False, 8)
        
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        vbox.pack_start(sw, True, True, 0)

        store = self.create_model()

        treeView = gtk.TreeView(store)
        treeView.connect("row-activated", self.on_activated)
        treeView.set_rules_hint(True)
        sw.add(treeView)

        self.create_columns(treeView)
        self.statusbar = gtk.Statusbar()
        
        vbox.pack_start(self.statusbar, False, False, 0)

        self.add(vbox)
        self.show_all()


    def create_model(self):
        store = gtk.ListStore(str, str, str, str, str)
        self.code = init_domain_list()
        if self.code == 1:
            for act in domain_list:
                store.append([act[0], act[1], act[2], act[3], act[4],])
            return store
        else:
            return store


        


    def create_columns(self, treeView):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("域名", rendererText, text=0)
        column.set_sort_column_id(0)
        treeView.append_column(column)
        
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("域名等级", rendererText, text=1)
        column.set_sort_column_id(1)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("状态", rendererText, text=2)
        column.set_sort_column_id(2)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("记录数", rendererText, text=3)
        column.set_sort_column_id(3)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("ID", rendererText, text=4)
        column.set_sort_column_id(4)
        treeView.append_column(column)


    def on_activated(self, widget, row, col):
        
        model = widget.get_model()
        text = model[row][0] + ", " + model[row][1] + ", " + model[row][2]
        self.statusbar.push(0, text)

    def main(self):
        text = str(self.code)
        self.statusbar.push(0, text)
        gtk.main()

if __name__ == '__main__':
    mainwindow = PyApp()
    mainwindow.main()
    
    





