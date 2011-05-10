#!/usr/bin/env python
# coding=utf-8

# Released under GPLv3.
# Author : iceleaf <iceleaf916@gmail.com>

import gtk

class MainWindow():
    def __init__ (self):
        # get the glade file
        self.builder = gtk.Builder()
        self.builder.add_from_file("main.glade")

        self.window = self.builder.get_object("window")
        self.window.set_icon_from_file("dnspod.png")
        
        # get menu item objects
        self.login = self.builder.get_object("login")
        self.quit = self.builder.get_object("quit")
        self.help_about = self.builder.get_object("help_about")

        # get treeview object 
        self.treeview = self.builder.get_object("treeview")
        self.treeview.connect("row-activated", self.on_modify_records)
        self.treeview.set_rules_hint(True)

        self.domainstore = gtk.ListStore(str, str, str, str, str)
        self.treeview.set_model(self.domainstore)
        self.create_columns(self.treeview)

        self.login_dialog = self.builder.get_object("login_dialog")
        self.about_dialog = self.builder.get_object("about_dialog")
        self.records_dialog = self.builder.get_object("records_dialog")

        self.help_about.connect("activate", self.on_about_dialog)
        self.window.connect("destroy", gtk.main_quit)
        self.quit.connect("activate", gtk.main_quit)
        self.login.connect("activate", self.on_login_dialog)

        self.window.show()

        gtk.main()

    def on_login_dialog(self, widget):
        response = self.login_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.domainstore.append(["yks.me", "免费", "启用", "7", "1233434"])
        
        self.login_dialog.hide()

    def on_about_dialog (self, widget):
        self.about_dialog.run()
        self.about_dialog.hide()
        

    def on_modify_records(self, widget, row, col):
        self.records_dialog.run()
        self.records_dialog.hide()
        

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
        

if __name__ == "__main__":
    main = MainWindow()
