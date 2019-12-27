#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__version__ = '1.0.0'
__date__ = '2018-05-01'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import os
from smb.SMBConnection import SMBConnection


class Connect(object):

    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    def list_content(self, service_name, path):
        samba = SMBConnection(self.username, self.password, '', '')
        samba.connect(self.ip, self.port)
        try:
            content = 'type\tname\n----\t----\n'
            for files in samba.listPath(service_name, path)[2:]:
                if samba.getAttributes(service_name, path.rstrip('/') + '/' + files.filename).isDirectory:
                    content += ('d\t%s\n' % files.filename)
                else:
                    content += ('f\t%s\n' % files.filename)
            else:
                return content[:-1]
        except Exception:
            print('retrieve content failure! ')
        finally:
            samba.close()

    def make_directory(self, service_name, path):
        samba = SMBConnection(self.username, self.password, '', '')
        samba.connect(self.ip, self.port)
        try:
            samba.createDirectory(service_name, path)
        except Exception:
            print('create directory failure! ')
        else:
            print('create directory success! ')
        finally:
            samba.close()

    def samba_put(self, service_name, localfile, remotefile):
        samba = SMBConnection(self.username, self.password, '', '')
        samba.connect(self.ip, self.port)

        def list_put(share_name, localstuff, remotestuff):
            dirname = os.path.dirname(remotestuff)
            basename = os.path.basename(remotestuff)
            data = []
            for value in samba.listPath(share_name, dirname):
                data.append(value.filename)
            else:
                if basename not in data:
                    samba.createDirectory(share_name, remotestuff)
            for content in os.listdir(localstuff):
                localpath = localstuff + os.sep + content
                remotepath = remotestuff + '/' + content
                if os.path.isfile(localpath):
                    handler = open(localpath, 'rb')
                    samba.storeFile(share_name, remotepath, handler)
                    handler.close()
                else:
                    list_put(share_name, localpath, remotepath)
        try:
            if os.path.isfile(localfile):
                handle = open(localfile, 'rb')
                samba.storeFile(service_name, remotefile, handle)
                handle.close()
            else:
                list_put(service_name, localfile, remotefile)
        except Exception:
            print('upload file failure! ')
        finally:
            samba.close()

    def samba_get(self, service_name, remotefile, localfile):
        samba = SMBConnection(self.username, self.password, '', '')
        samba.connect(self.ip, self.port)

        def list_get(share_name, remotestuff, localstuff):
            if os.path.isdir(localstuff) is False:
                os.mkdir(localstuff)
            for files in samba.listPath(share_name, remotestuff)[2:]:
                localpath = localstuff + os.sep + files.filename
                remotepath = remotestuff + '/' + files.filename
                if not samba.getAttributes(share_name, remotepath).isDirectory:
                    handler = open(localpath, 'wb')
                    samba.retrieveFile(share_name, remotepath, handler)
                    handler.close()
                else:
                    list_get(share_name, remotepath, localpath)
        try:
            if not samba.getAttributes(service_name, remotefile).isDirectory:
                handle = open(localfile, 'wb')
                samba.retrieveFile(service_name, remotefile, handle)
                handle.close()
            else:
                list_get(service_name, remotefile, localfile)
        except Exception:
            print('download file failure! ')
        finally:
            samba.close()
