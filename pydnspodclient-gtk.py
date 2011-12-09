#!/usr/bin/python
import pygtk
pygtk.require("2.0")
import gtk

if __name__ == '__main__':
    from pydnspodclient import pydnspodclient
    gtk.gdk.threads_init()
    app = pydnspodclient.MainWindow()
    gtk.main()
