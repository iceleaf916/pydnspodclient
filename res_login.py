#!/usr/bin/env python
# - * - coding: utf-8 - * -

import gtk
import urllib
import urllib2
import json

user_mail = ''
password = ''

user_agent = 'PyDNSPodClient/0.0.2(iceleaf916@gmail.com)'

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

class LoginWindow():
    def __init__ (self):       
        self.builder = gtk.Builder()
        self.builder.add_from_file("login_window.glade")
        self.window = self.builder.get_object("login_window")
        self.user_mail = self.builder.get_object("email")
        self.password = self.builder.get_object("passwd")
        self.login_button = self.builder.get_object("login")

        self.login_button.connect("clicked", self.login_get_list)

        self.window.connect("destroy", gtk.main_quit)
        self.window.set_title("登录到DNSPod")
        try:
            self.window.set_icon_from_file("dnspod.png")
        except Exception, e:
            print e.message
        
        self.password.set_visibility(False)

        self.window.show()
        gtk.main()

    def login_get_list(self, widget):
        user_mail = self.user_mail.get_text()
        password = self.password.get_text()
        print password
        self.dnspod_api = DnspodApi()
        domain_list_js = self.dnspod_api.getDomainList()
        if domain_list_js.get("status").get("code") == '1' :
            for y in domain_list_js.get("domains"):
                a = (y.get("name"), y.get("grade"), y.get("status"), int(y.get("records")), y.get("id"))
                domain_list.append(a)
            gtk.main_quit()
            DomainList()
        else:
            print domain_list_js.get("status").get("code")

    def OnQuit(self):
        gtk.main_quit()

class DomainList():
    def __init__(self):
        self.window = gtk.Window()
        self.window.set_size_request(680, 450)
        self.window.set_position(gtk.WIN_POS_CENTER)

        self.window.set_title("PyDNDPod Client")
        try:
            self.window.set_icon_from_file("dnspod.png")
        except Exception, e:
            print e.message
        self.window.connect("destroy", gtk.main_quit)

        vbox = gtk.VBox(False, 0)

        #add menubar
        menubar = gtk.MenuBar()
        filemenu = gtk.Menu()
        filem = gtk.MenuItem("File")
        filem.set_submenu(filemenu)
               
        exit = gtk.MenuItem("Exit")
        exit.connect("activate", self.update_store)
        filemenu.append(exit)

        menubar.append(filem)
        vbox.pack_start(menubar, False, False, 0)
        #add menubar

        #add toolbar
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)

        addbutton = gtk.ToolButton(gtk.STOCK_ADD)
        delbutton = gtk.ToolButton(gtk.STOCK_DELETE)
        editbutton = gtk.ToolButton(gtk.STOCK_EDIT)
        stopbutton = gtk.ToolButton(gtk.STOCK_STOP)

        toolbar.insert(addbutton, 0)
        toolbar.insert(delbutton, 1)
        toolbar.insert(editbutton, 2)
        toolbar.insert(stopbutton, 3)

        vbox.pack_start(toolbar, False, False, 0)
        #add toolbar

        #add domain list treeview
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)            

        self.domainstore = gtk.ListStore(str, str, str, str, str)
        

        treeView = gtk.TreeView(self.domainstore)
        treeView.connect("row-activated", self.on_activated)
        treeView.set_rules_hint(True)
        sw.add(treeView)
        
        self.create_columns(treeView)

        vbox.pack_start(sw, True, True, 0)
        #add domain list treeview

        #add status bar
        self.statusbar = gtk.Statusbar()
        vbox.pack_start(self.statusbar, False, False, 0)
        #add status bar      
        
        self.window.add(vbox)
        self.window.show_all()

        self.update_store()
        gtk.main() 

    def create_columns(self, treeView):
    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("域名", rendererText, text=0)
        column.set_sort_column_id(0)
        column.set_resizable(True)
        column.set_min_width(200)
        treeView.append_column(column)
        
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("域名等级", rendererText, text=1)
        column.set_sort_column_id(1)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("状态", rendererText, text=2)
        column.set_sort_column_id(2)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("记录数", rendererText, text=3)
        column.set_sort_column_id(3)
        column.set_resizable(True)
        treeView.append_column(column)

        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("ID", rendererText, text=4)
        column.set_sort_column_id(4)
        column.set_resizable(True)
        treeView.append_column(column)

    def update_store(self):        
        for act in domain_list:
            self.domainstore.append([act[0], act[1], act[2], act[3], act[4],])
            self.statusbar.push(1, "连接成功！")
    def on_activated():
        pass
        

class DnspodApi():
    def __init__ (self):
        self.headers = { 'User-Agent' : user_agent }
        self.values = {'login_email' : user_mail,
          'login_password' : password,
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

if __name__ == '__main__':
    mainwindow = LoginWindow()
