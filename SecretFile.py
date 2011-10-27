#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import base64
import pyDes
from const import key

class SecretFile():
    def __init__(self):
        self.three_des = pyDes.triple_des(key, mode=pyDes.CBC, 
                                          IV="\0\1\2\3\4\5\6\7", pad=None, 
                                          padmode=pyDes.PAD_PKCS5)
        saved_file_dir = os.path.expanduser("~")
        self.saved_file = os.path.join(saved_file_dir, ".dnspod.db")
        if not os.path.exists(self.saved_file):
            fp = open(self.saved_file, "w")
            fp.close()

    def encrypt(self, data):
        en = self.three_des.encrypt(data)
        return base64.b64encode(en)
    
    def decrypt(self, data):
        de = base64.b64decode(data)
        return self.three_des.decrypt(de)

    def get(self):
        fp = open(self.saved_file, "r")
        return_data = []
        while 1:
            line = fp.readline()
            if line:
                data = self.decrypt(line)
                return_data.append(data)
            else:
                break
        return return_data
            
    def save(self, user_mail, password):
        a = self.encrypt(user_mail)
        b = self.encrypt(password)
        saved_data = a + "\n" + b
        fp = open(self.saved_file, "w")
        fp.write(saved_data)
        fp.close()
        
    def clear(self):
        a=""
        fp = open(self.saved_file, "w")
        fp.write(a)
        fp.close()

def test ():
    pass

if __name__ == "__main__":
    test()
