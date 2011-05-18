#!/usr/bin/env python
# coding=utf-8

#
# Copyright (C) 2011 iceleaf <iceleaf916@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

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

import os
import gtk
import urllib
import urllib2
import json

class MainWindow():
    def __init__ (self): 
        main_dir = os.path.dirname(__file__)
        glade_file = os.path.join(main_dir, "main.glade")
        logo_file = os.path.join(main_dir, "dnspod.png")
        db_file = os.path.join(main_dir, "dnspod.db")
        # get the glade file
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)

        self.window = self.builder.get_object("window")
        self.window.set_icon_from_file(logo_file)
        
        # get menu item objects
        self.login = self.builder.get_object("login")
        self.quit = self.builder.get_object("quit")
        self.help_about = self.builder.get_object("help_about")
        
        self.add_domain = self.builder.get_object("add_domain")
        self.delete_domain = self.builder.get_object("delete_domain")
        self.add_record = self.builder.get_object("add_record")
        self.delete_record = self.builder.get_object("delete_record")
        self.edit_record = self.builder.get_object("edit_record")

        # get label object
        self.record_label = self.builder.get_object("record_label")

        # get domain_treeview object
        self.domain_treeview = self.builder.get_object("domain_treeview")       
        
        self.domain_store = gtk.ListStore(str, str)
        self.domain_treeview.set_model(self.domain_store)
        self.domain_treeview.connect("row-activated", self.list_records)
        self.domain_treeview.set_rules_hint(True)
        self.create_domain_columns(self.domain_treeview)

        # get record_treeview object
        self.record_treeview = self.builder.get_object("record_treeview")

        self.record_store = gtk.ListStore(str, str, str, str, str, str, str, str)
        self.record_treeview.set_model(self.record_store)
        self.record_treeview.connect("row-activated", self.do_edit_record)
        self.record_treeview.connect("button-press-event", self.on_button_press_menu)
        self.create_record_columns(self.record_treeview)

        # get all dialog objects
        self.login_dialog = self.builder.get_object("login_dialog")
        self.login_dialog.set_icon_from_file(logo_file)
        self.about_dialog = self.builder.get_object("about_dialog")
        self.about_dialog.set_version("v" + VERSION)
        self.about_dialog.set_icon_from_file(logo_file)
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        self.about_dialog.set_logo(logo)
        self.error_dialog = self.builder.get_object("error_dialog")
        self.add_domain_dialog = self.builder.get_object("add_domain_dialog")
        self.add_domain_entry = self.builder.get_object("add_domain_entry")
        
        # get record edit dialog and it's child widget
        self.record_edit_dialog = self.builder.get_object("record_edit_dialog")
        self.record_name_entry = self.builder.get_object("record_name_entry")
        self.record_domain_label = self.builder.get_object("record_domain_label")
        self.record_type_box = self.builder.get_object("record_type_box")
        self.record_line_box = self.builder.get_object("record_line_box")
        self.record_value_entry = self.builder.get_object("record_value_entry")
        self.record_mx_entry = self.builder.get_object("record_mx_entry")
        self.record_ttl_entry = self.builder.get_object("record_ttl_entry")
       
        # get login and password object
        self.user_mail = self.builder.get_object("user_mail")
        self.password = self.builder.get_object("password")
        self.remember_password = self.builder.get_object("remember_password")

        # get main_statusbar object
        self.main_statusbar = self.builder.get_object("main_statusbar")
        self.main_statusbar.push(0, "欢迎使用PyDNSPod Client！")

        # binding the singel
        self.help_about.connect("activate", self.on_about_dialog)
        self.window.connect("destroy", gtk.main_quit)
        self.quit.connect("activate", gtk.main_quit)
        self.login.connect("activate", self.is_login_or_out)

        self.edit_record.connect("activate", self.menu_do_edit_record)
        self.delete_record.connect("activate", self.menu_do_delete_record)
        self.add_record.connect("activate", self.menu_do_add_record)
        self.add_domain.connect("activate", self.menu_do_add_doamin)
        self.delete_domain.connect("activate", self.menu_do_delete_domain)

        #init record types and lines store
        global record_types
        global record_lines
        self.record_type_store = gtk.ListStore(str)
        for a in record_types:
            self.record_type_store.append([a])
        self.record_line_store = gtk.ListStore(str)
        for b in record_lines:
            self.record_line_store.append([b])

        self.create_record_types(self.record_type_box)
        self.create_record_lines(self.record_line_box)
        mx_adjustment = gtk.Adjustment(0, 0, 20, 1, 10, 0)
        self.record_mx_entry.set_adjustment(mx_adjustment)
        ttl_adjustment = gtk.Adjustment(600, 1, 604800, 1, 10, 0)
        self.record_ttl_entry.set_adjustment(ttl_adjustment)

        self.window.show()

        gtk.main()

    def is_login_or_out(self, widget):
        if self.login.get_label() == "登录":
            self.on_login_dialog(widget)
        else:
            self.login_out(widget)        

    def on_login_dialog(self, widget):
        global domain_id_dict
        while 1:
            response = self.login_dialog.run()
            if response == gtk.RESPONSE_OK:
                global USER_MAIL
                global PASSWORD
                USER_MAIL = self.user_mail.get_text()
                PASSWORD = self.password.get_text()
                if self.remember_password.get_active() == True:
                    self.save_user_password(USER_MAIL, PASSWORD)
                self.dnspod_api = DnspodApi()
                self.domain_list_js = self.dnspod_api.getDomainList()
                if str(self.domain_list_js.get("status").get("code")) == "1":
                    for y in self.domain_list_js.get("domains"):
                        if y.get("status") == "enable":
                            self.domain_status = "正常"
                        else:
                            self.domain_status = "异常"                        
                        a = (y.get("name"), self.domain_status)
                        domain_id_dict[y.get("name")] = y.get("id")
                        self.domain_store.append(a)
                    self.login_dialog.hide()
                    self.login.set_label("注销")
                    self.main_statusbar.push(1, "登录成功！")
                    break
                else:
                    error_text = "出错了，错误信息：" + self.domain_list_js.get("status").get("message")
                    self.display_error(widget, error_text)
            elif response == gtk.RESPONSE_DELETE_EVENT or gtk.RESPONSE_CANCEL:
                break

        self.main_statusbar.push(4, "欢迎使用PyDNSPod Client！")
        self.login_dialog.hide()

    def on_about_dialog (self, widget):
        self.about_dialog.run()
        self.about_dialog.hide()
        
    def login_out(self, widget):
        self.record_store.clear()
        self.domain_store.clear()
        self.login.set_label("登录")
        self.main_statusbar.push(2, "已注销！")

    def list_records(self, widget, row, col):
        model = widget.get_model()
        self.pre_domain = model[row][0]
        text = self.pre_domain + " 的记录列表"
        self.main_statusbar.push(0, "当前操作域名：" + self.pre_domain)
        self.record_label.set_text(text)
        self.domain_id = domain_id_dict[self.pre_domain]

        record_list_js = self.dnspod_api.getRecordList(self.domain_id)
        if str(record_list_js.get("status").get("code")) == "1":
            self.record_store.clear()
            for b in record_list_js.get("records"):
                if b.get("enabled") == "1":
                    self.record_status = "是"
                else:
                    self.record_status = "否" 
                a = (b.get("name"), b.get("type"), b.get("line"), b.get("value"), 
                     b.get("mx"), b.get("ttl"), self.record_status, b.get("id") )
                self.record_store.append(a)
        else:
            self.record_store.clear()
            error_text = "出错了，错误信息：" + record_list_js.get("status").get("message")
            self.display_error(widget, error_text)

    def do_edit_record(self, widget, row, col):
        model = self.record_treeview.get_model() 
        self.record_edit_dialog.set_title("编辑记录 @ (" + self.pre_domain + ")")

        self.record_name_entry.set_text(model[row][0])
        self.record_domain_label.set_text("." + self.pre_domain)

        self.record_type_box.set_active(self.record_types_dict.get(model[row][1]))
        self.record_line_box.set_active(self.record_lines_dict.get(model[row][2]))

        self.record_value_entry.set_text(model[row][3])

        self.record_mx_entry.set_value(int(model[row][4]))
        self.record_ttl_entry.set_value(int(model[row][5]))
        
        while 1:                      
            response = self.record_edit_dialog.run()
            if response == gtk.RESPONSE_OK:
                a = self.record_name_entry.get_text()
                b = self.record_type_box.get_active_text()
                c = self.record_line_box.get_active_text()
                d = self.record_value_entry.get_text()
                e = str(int(self.record_mx_entry.get_value()))
                f = str(int(self.record_ttl_entry.get_value()))
                record_modify_result_js = self.dnspod_api.recordModify(self.domain_id, model[row][7], a, b, c, d, e, f)
                if str(record_modify_result_js.get("status").get("code")) == "1":
                    self.main_statusbar.push(3, "记录修改成功！")
                    self.record_edit_dialog.hide()
                    model[row][0], model[row][1], model[row][2], model[row][3], model[row][4], model[row][5] = a, b, c, d, e, f
                    break
                else:
                    error_text = "出错了，错误信息：" + record_modify_result_js.get("status").get("message")
                    self.display_error(widget, error_text)
            else:
                self.main_statusbar.push(4, "欢迎使用PyDNSPod Client！")
                self.record_edit_dialog.hide()
                break
       
    def create_record_types(self, widget):
        cell = gtk.CellRendererText()
        self.record_type_box.set_model(self.record_type_store)
        self.record_type_box.pack_start(cell, True)
        self.record_type_box.add_attribute(cell, "text", 0)
        self.record_type_box.set_active(0)
        self.record_types_dict = { "A" : 0,
                                  "CNAME" : 1,
                                  "MX" : 2,
                                  "URL" : 3,
                                  "NS" : 4,
                                  "TXT" : 5,
                                  "AAAA" : 6 }

    def create_record_lines(self, widget):
        cell = gtk.CellRendererText()
        self.record_line_box.set_model(self.record_line_store)
        self.record_line_box.pack_start(cell, True)
        self.record_line_box.add_attribute(cell, "text", 0)
        self.record_line_box.set_active(0)
        self.record_lines_dict = { "默认" : 0,
                                  "电信" : 1,
                                  "联通" : 2,
                                  "教育网" : 3 }

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

    def save_user_password(self, user_mail, password):
        pass

    def on_button_press_menu(self, widget, event, data = None):
        if event.button == 3:
            model, rows = widget.get_selection().get_selected_rows()

    def return_widget_row(self, widget):
        model, rows = widget.get_selection().get_selected_rows()
        if rows <> []:
            return (model, rows)
        else:
            if widget == self.record_treeview:
                error_text = "请您选择一条记录！"
            else:
                error_text = "请您选择一个域名！"
            self.display_error(widget, error_text)
            return (-1, [(-1,)])
        
    def display_error(self, widget, text):
        error_text = text
        self.error_dialog.set_markup(error_text)
        self.error_dialog.run()
        self.error_dialog.hide()

    def menu_do_add_record(self, widget):
        if self.login.get_label() == "登录":
            text = "请您先登录！"
            self.display_error(self.window, text)
        else:
            model, rows = self.return_widget_row(self.domain_treeview)
            row = rows[0][0]
            if row <> -1:
                domain = model[row][0]
                while 1:
                    self.record_edit_dialog.set_title("添加记录 @ (" + domain + ")")

                    self.record_name_entry.set_text("")
                    self.record_domain_label.set_text("." + domain)

                    self.record_type_box.set_active(0)
                    self.record_line_box.set_active(0)

                    self.record_value_entry.set_text("")

                    self.record_mx_entry.set_value(0)
                    self.record_ttl_entry.set_value(600)
                    response = self.record_edit_dialog.run()
                    if response == gtk.RESPONSE_OK:
                        self.domain_id = domain_id_dict[domain]
                        a = self.record_name_entry.get_text()
                        b = self.record_type_box.get_active_text()
                        c = self.record_line_box.get_active_text()
                        d = self.record_value_entry.get_text()
                        e = str(int(self.record_mx_entry.get_value()))
                        f = str(int(self.record_ttl_entry.get_value()))
                        record_create_result_js = self.dnspod_api.createRcord(self.domain_id, a, b, c, d, e, f)
                        if str(record_create_result_js.get("status").get("code")) == "1":
                            self.main_statusbar.push(3, "记录添加成功！")
                            self.record_edit_dialog.hide()
                            new_record = (a, b, c, d, e, f, "是", record_create_result_js.get("record").get("id") )
                            self.record_store.append(new_record)
                            break
                        else:
                            error_text = "出错了，错误信息：" + record_create_result_js.get("status").get("message")
                            self.display_error(widget, error_text)
                    else:
                        self.main_statusbar.push(4, "欢迎使用PyDNSPod Client！")
                        self.record_edit_dialog.hide()
                        break
            
    
    def menu_do_edit_record(self, widget):
        model, rows = self.return_widget_row(self.record_treeview)
        row = rows[0][0]
        if row <> -1:
            self.do_edit_record(self.record_treeview, row, col=0)

    def menu_do_delete_record(self, widget):
        model, rows = self.return_widget_row(self.record_treeview)
        row = rows[0][0]
        if row <> -1:
            self.do_delete_record(self.record_treeview, model, rows)

    def do_delete_record(self, widget, model, rows):
        row = rows[0][0]
        record_delete_js = self.dnspod_api.recordRemove(self.domain_id, model[row][7])
        if str(record_delete_js.get("status").get("code")) == "1":
            text = self.pre_domain + " 的记录 " + model[row][0] + " 删除成功！"
            self.main_statusbar.push(0, text)
            self.record_store.remove(model.get_iter(rows[0]))
        else:
            text = "出错了，错误信息：" + record_delete_js.get("status").get("message")
            self.display_error(self.window, text)

    def menu_do_add_doamin(self, widget):
        if self.login.get_label() == "登录":
            text = "请您先登录！"
            self.display_error(self.window, text)
        else:
            while 1:
                response = self.add_domain_dialog.run()
                if response == gtk.RESPONSE_OK:
                    domain = self.add_domain_entry.get_text()           
                    add_domain_result_js = self.dnspod_api.createDomain(domain)
                    if str(add_domain_result_js.get("status").get("code")) == "1":
                        global domain_id_dict
                        text = "域名：" + domain + " 添加成功！"
                        self.main_statusbar.push(0, text)
                        new_domain = (domain, "已启用")
                        self.domain_store.append(new_domain)
                        domain_id_dict[domain] = add_domain_result_js.get("domain").get("id")
                        break
                    else:
                        error_text = "出错了，错误信息：" + add_domain_result_js("status").get("message")
                        self.display_error(self.window, error_text)
                elif response == gtk.RESPONSE_DELETE_EVENT or gtk.RESPONSE_CANCEL:
                    break

            self.add_domain_dialog.hide()

    def menu_do_delete_domain(self, widget):
        model, rows = self.return_widget_row(self.domain_treeview)
        row = rows[0][0]
        if row <> -1:
            self.do_delete_domain(self.domain_treeview, model, rows)

    def do_delete_domain(self, widget, model, rows):
        row = rows[0][0]
        domain_remove_iter = model.get_iter(rows[0])
        domain = model[row][0]
        domain_delete_result_js = self.dnspod_api.removeDomain(domain_id_dict[domain])
        if str(domain_delete_result_js.get("status").get("code")) == "1":
            text = '域名"' + domain + '"删除成功！'
            self.main_statusbar.push(0, text)
            self.domain_store.remove(domain_remove_iter)
        else:
            text = "出错了，错误信息：" + domain_delete_result_js.get("status").get("message")
            self.display_error(self.window, text)
                               
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

    def recordModify(self, domain_id, record_id, sub_domain, record_type, record_line, record_value, record_mx, record_ttl):
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
        record_mod_req = urllib2.Request(record_mod_url, data, self.headers)
        response = urllib2.urlopen(record_mod_req)
        js = response.read()
        return json.loads(js)

    def recordRemove(self, domain_id, record_id):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        temp_values['record_id'] = record_id
        data = urllib.urlencode(temp_values)
        record_remove_req = urllib2.Request(record_remove_url, data, self.headers)
        response = urllib2.urlopen(record_remove_req)
        js = response.read()
        return json.loads(js)

    def createRcord(self, domain_id, sub_domain, record_type, record_line, record_value, record_mx, record_ttl):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        temp_values['sub_domain'] = sub_domain
        temp_values['record_type'] = record_type
        temp_values['record_line'] = record_line
        temp_values['value'] = record_value
        temp_values['mx'] = record_mx
        temp_values['ttl'] = record_ttl
        data = urllib.urlencode(temp_values)
        record_cre_req = urllib2.Request(record_cre_url, data, self.headers)
        response = urllib2.urlopen(record_cre_req)
        js = response.read()
        return json.loads(js)
        
    def createDomain(self, domain):
        temp_values = self.values.copy()
        temp_values['domain'] = domain
        data = urllib.urlencode(temp_values)
        domain_cre_req = urllib2.Request(domain_cre_url, data, self.headers)
        js = urllib2.urlopen(domain_cre_req).read()
        return json.loads(js)

    def removeDomain(self, domain_id):
        temp_values = self.values.copy()
        temp_values['domain_id'] = domain_id
        data = urllib.urlencode(temp_values)
        domain_remove_req = urllib2.Request(domain_remove_url, data, self.headers)
        js = urllib2.urlopen(domain_remove_req).read()
        return json.loads(js)
        
if __name__ == "__main__":
    main = MainWindow()
