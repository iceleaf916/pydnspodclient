#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk
import threading
from const import *
from dnspodapi import DnspodApi
from secretfile import SecretFile

global result_js
global spinner_flag
spinner_flag = False

class MainWindow():
    '''主窗口类'''
    
    def __init__ (self):
        '''构造函数'''

        
        # get the glade file
        self.builder = gtk.Builder()
        self.builder.add_from_file(GLADE_FILE)
        self.builder.connect_signals(self)
        for widget in self.builder.get_objects():
            if issubclass(type(widget), gtk.Buildable):
                name = gtk.Buildable.get_name(widget)
                setattr(self, name, widget)
        
        self.init_mainwindow()
        self.init_domain_list()
        self.init_record_list()
        self.init_login_dialog()
        self.init_record_types_lines()
        self.init_record_edit_dialog()
        
        self.edit_record.connect("activate", self.menu_do_edit_record)
        self.delete_record.connect("activate", self.menu_do_delete_record)
        self.add_record.connect("activate", self.menu_do_add_record)
        self.add_domain.connect("activate", self.menu_do_add_doamin)
        self.delete_domain.connect("activate", self.menu_do_delete_domain)

        self.window.show_all()
        self.spinner.hide()
        wait_spinner_flag_thread = WaitForSpinnerFlag(self.spinner)
        wait_spinner_flag_thread.setDaemon(True)
        wait_spinner_flag_thread.start()

    def init_mainwindow(self):
        '''初始化主窗口'''
        
        self.window.set_icon_from_file(LOGO_FILE)
        self.window.hided = False
        
        # 状态栏
        self.main_statusbar.push(0, "欢迎使用PyDNSPod Client！")

    def init_domain_list(self):
        '''初始化域名列表'''
        
        self.domain_store = gtk.ListStore(str, str)
        self.domain_treeview.set_model(self.domain_store)
        self.domain_treeview.connect("row-activated", self.list_records)
        self.domain_treeview.set_rules_hint(True)
        self.create_domain_columns(self.domain_treeview)
        
    def init_record_list(self):
        '''初始化记录列表'''
        
        self.record_store = gtk.ListStore(str, str, str, str, str, str, str, str)
        self.record_treeview.set_model(self.record_store)
        self.record_treeview.connect("row-activated", self.do_edit_record)
        self.record_treeview.connect("button-press-event", \
            self.on_button_press_menu)
        self.create_record_columns(self.record_treeview)
        
    def init_login_dialog(self):
        '''初始化登录对话框'''
        
        self.login_dialog.set_icon_from_file(LOGO_FILE)

    def init_record_types_lines(self):
        '''初始化记录类型及线路'''
        
        self.record_type_store = gtk.ListStore(str)
        for a in RECORD_TYPES:
            self.record_type_store.append([a])
        self.record_line_store = gtk.ListStore(str)
        for b in RECORD_LINES:
            self.record_line_store.append([b])
            
    def init_record_edit_dialog(self):
        '''初始化记录编辑列表'''
        
        self.create_record_types(self.record_type_box)
        self.create_record_lines(self.record_line_box)
        mx_adjustment = gtk.Adjustment(0, 0, 20, 1, 10, 0)
        self.record_mx_entry.set_adjustment(mx_adjustment)
        ttl_adjustment = gtk.Adjustment(600, 1, 604800, 1, 10, 0)
        self.record_ttl_entry.set_adjustment(ttl_adjustment)
        
    def on_mainwin_delete_event(self, widget, data=None):
        '''关闭窗口事件'''
        
        gtk.main_quit()

    def on_quit_menuitem_activate(self, widget, data=None):
        '''退出菜单项目激活事件'''
        
        gtk.main_quit()

    def is_login_or_out(self, widget):
        '''判断登录状态'''

        if self.login.get_label() == "登录":
            self.on_login_dialog(widget)
        else:
            self.login_out(widget)

    def on_login_dialog(self, widget):

        '''显示登录窗口'''
        
        self.secret_file = SecretFile()
        return_data = self.secret_file.get()

        if return_data <> []:
            saved_user_mail, saved_password = return_data[0], return_data[1]
        else:
            saved_user_mail = ""
            saved_password = ""
        self.user_mail.set_text(saved_user_mail)
        self.password.set_text(saved_password)

        response = self.login_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.login_button_clicked()
        self.login_dialog.hide()

    def login_button_clicked (self):
        user_mail = self.user_mail.get_text()
        user_passwd = self.password.get_text()
        if self.remember_password.get_active() == True:
            self.secret_file.save(user_mail, user_passwd)
        else:
            self.secret_file.clear()
        self.dnspod_api = DnspodApi(user_mail, user_passwd, CLIENT_AGENT)
        self.main_statusbar.push(0, "正在登录中...")
        global spinner_flag
        spinner_flag = True
        fetch_thread = FetchDNSPodData(self.dnspod_api.getDomainList, (), \
                                        self.after_login_button_clicked, ())
        fetch_thread.setDaemon(True)
        fetch_thread.start()

    def after_login_button_clicked(self):
        global domain_id_dict
        global result_js
        global spinner_flag
        spinner_flag = False
        if str(result_js.get("status").get("code")) == "1":
            for y in result_js.get("domains"):
                if y.get("status") == "enable":
                    self.domain_status = "正常"
                else:
                    self.domain_status = "异常"
                a = (y.get("name"), self.domain_status)
                self.domain_store.append(a)
                domain_id_dict[y.get("name")] = y.get("id")
            self.login.set_label("注销")
            self.main_statusbar.push(0, "登录成功！")
        else:
            error_text = "登录失败，错误信息：" + \
                result_js.get("status").get("message")
            self.display_error(self.window, error_text)
            self.main_statusbar.push(0, "登录失败！")

    def on_about_dialog (self, widget):
        '''创建关于对话框'''

        about = gtk.AboutDialog()
        logo = gtk.gdk.pixbuf_new_from_file(LOGO_FILE)
        about.set_name("PyDNSPod Client")
        about.set_version("v" + VERSION)
        about.set_icon(logo)
        about.set_logo(logo)
        about.set_authors(["iceleaf <iceleaf916@gmail.com>"])
        about.set_website("https://github.com/iceleaf916/pydnspodclient")
        about.set_website_label("项目主页")
        about.set_comments("一个DNSPod的Python客户端")
        about.set_copyright("Copyright (C) 2011 PyDNDPod Client")
        about.set_license(license)
        about.set_wrap_license(True)
        about.set_transient_for(self.window)
        about.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        about.run()
        about.destroy()
        
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
        error_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE)
        error_dialog.set_position = (gtk.WIN_POS_CENTER_ON_PARENT)
        
        error_dialog.set_markup(error_text)
        error_dialog.run()
        error_dialog.destroy()

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


class WaitForSpinnerFlag(threading.Thread):
    def __init__ (self, spinner):
        threading.Thread.__init__(self, name="WaitForSpinnerFlag")
        self.spinner = spinner

    def run (self):
        global spinner_flag
        while 1:
            self.spinner_active = self.spinner.get_property("active")
            if spinner_flag <> self.spinner_active:
                if self.spinner_active:
                    self.spinner.hide()
                    self.spinner.stop()
                else:
                    self.spinner.start()
                    self.spinner.show()

class FetchDNSPodData(threading.Thread):
    def __init__ (self, func, args, func2, args2):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.func2 = func2
        self.args2 = args2

    def run (self):
        global result_js
        global spinner_flag
        self.res = apply(self.func, self.args)
        result_js = self.res
        spinner_flag = False
        apply(self.func2, self.args2)


if __name__ == "__main__":
    gtk.gdk.threads_init()
    app = MainWindow()
    gtk.main()
