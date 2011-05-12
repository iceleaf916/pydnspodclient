#!/usr/bin/env python
# coding=utf-8

# Released under GPLv3.
# Author : iceleaf <iceleaf916@gmail.com>

USER_MAIL = ''
PASSWORD = ''

VERSION = "0.0.4"

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


import gtk
import urllib
import urllib2
import json

class MainWindow():
    def __init__ (self):
        # get the glade file
        self.builder = gtk.Builder()
        self.builder.add_from_file("newmain.glade")

        self.window = self.builder.get_object("window")
        self.window.set_icon_from_file("dnspod.png")
        
        # get menu item objects
        self.login = self.builder.get_object("login")
        self.quit = self.builder.get_object("quit")
        self.help_about = self.builder.get_object("help_about")

        # get label object
        self.record_label = self.builder.get_object("record_label")

        # get domain_treeview object 
        self.domain_treeview = self.builder.get_object("domain_treeview")       
        
        self.domain_store = gtk.ListStore(str, str)
        self.domain_treeview.set_model(self.domain_store)
        self.domain_treeview.connect("row-activated", self.on_modify_records)
        self.domain_treeview.set_rules_hint(True)
        self.create_domain_columns(self.domain_treeview)

        # get record_treeview object
        self.record_treeview = self.builder.get_object("record_treeview")

        self.record_store = gtk.ListStore(str, str, str, str, str, str, str, str)
        self.record_treeview.set_model(self.record_store)
        self.create_record_columns(self.record_treeview)

        # get all dialog objects
        self.login_dialog = self.builder.get_object("login_dialog")
        self.about_dialog = self.builder.get_object("about_dialog")
        self.error_dialog = self.builder.get_object("error_dialog")
        
        # get login and password object
        self.user_mail = self.builder.get_object("user_mail")
        self.password = self.builder.get_object("password")

        # get main_statusbar object
        self.main_statusbar = self.builder.get_object("main_statusbar")
        self.main_statusbar.push(0, "欢迎使用PyDNSPod Client！")

        # binding the singel
        self.help_about.connect("activate", self.on_about_dialog)
        self.window.connect("destroy", gtk.main_quit)
        self.quit.connect("activate", gtk.main_quit)
        self.login.connect("activate", self.is_login_or_out)

        self.window.show()

        gtk.main()

    def is_login_or_out(self, widget):
        if self.login.get_label() == "登录":
            self.on_login_dialog(widget)
        else:
            self.login_out(widget)        

    def on_login_dialog(self, widget):        
        while 1:
            response = self.login_dialog.run()
            if response == gtk.RESPONSE_OK:
                global USER_MAIL
                global PASSWORD
                USER_MAIL = self.user_mail.get_text()
                PASSWORD = self.password.get_text()
                self.dnspod_api = DnspodApi()
                self.domain_list_js = self.dnspod_api.getDomainList()
                if str(self.domain_list_js.get("status").get("code")) == "1":
                    for y in self.domain_list_js.get("domains"):
                        a = (y.get("name"), y.get("status"))
                        self.domain_store.append(a)
                    self.login_dialog.hide()
                    self.login.set_label("注销")
                    self.main_statusbar.push(1, "登录成功！")
                    break
                else:
                    text = "登录失败！ 错误代码:" + str(self.domain_list_js.get("status").get("code"))
                    self.error_dialog.set_markup(text)
                    self.error_dialog.run()
                    self.error_dialog.destroy()
            else:
                self.login_dialog.hide()
                break

    def on_about_dialog (self, widget):
        self.about_dialog.run()
        self.about_dialog.hide()
        
    def login_out(self, widget):
        self.record_store.clear()
        self.domain_store.clear()
        self.login.set_label("登录")
        self.main_statusbar.push(2, "已注销！")

    def on_modify_records(self, widget, row, col):
        model = widget.get_model()
        text = model[row][0] + " 的记录列表"
        self.record_label.set_text(text)
        for d in self.domain_list_js.get("domains"):
            if d.get("name") == model[row][0]:
                self.domain_id = d.get("id")

        record_list_js = self.dnspod_api.getRecordList(self.domain_id)
        if str(record_list_js.get("status").get("code")) == "1":
            self.record_store.clear()
            for b in record_list_js.get("records"):
                a = (b.get("name"), b.get("type"), b.get("line"), b.get("value"), 
                     b.get("mx"), b.get("ttl"), b.get("enabled"), b.get("id") )
                self.record_store.append(a)
        else:
            error_text = "出错了，错误信息：" + record_list_js.get("status").get("message")
            self.error_dialog.set_markup(text)
            self.error_dialog.run()
            self.error_dialog.destroy()

    def create_domain_columns(self, treeView):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("域名", rendererText, text=0)
        column.set_sort_column_id(0)
        column.set_resizable(True)
        column.set_min_width(100)
        treeView.append_column(column)
        

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("状态", rendererText, text=1)
        column.set_sort_column_id(1)
        column.set_resizable(True)
        treeView.append_column(column)

    def create_record_columns(self, treeView):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("记录", rendererText, text=0)
        column.set_sort_column_id(0)
        column.set_resizable(True)
        column.set_min_width(100)
        treeView.append_column(column)
        

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("类型", rendererText, text=1)
        column.set_sort_column_id(1)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("线路", rendererText, text=2)
        column.set_sort_column_id(2)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("记录值", rendererText, text=3)
        column.set_sort_column_id(3)
        column.set_resizable(True)
        column.set_min_width(100)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("MX", rendererText, text=4)
        column.set_sort_column_id(4)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("TTL", rendererText, text=5)
        column.set_sort_column_id(5)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("启用？", rendererText, text=6)
        column.set_sort_column_id(6)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("ID", rendererText, text=7)
        column.set_sort_column_id(7)
        column.set_resizable(True)
        treeView.append_column(column)

        
        
class DnspodApi():
    def __init__ (self):
        global VERSION
        global USER_MAIL
        global PASSWORD
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

    def getRecordList(self, domain_id):
        temp_values = self.values.copy()
        temp_values['length'] = '30'
        temp_values['offset'] = '0'
        temp_values['domain_id'] = domain_id
        data = urllib.urlencode(temp_values)
        record_list_req = urllib2.Request(record_list_url, data, self.headers)
        response = urllib2.urlopen(record_list_req)
        js = response.read()
        return json.loads(js)

if __name__ == "__main__":
    main = MainWindow()
