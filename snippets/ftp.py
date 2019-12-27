#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__version__ = '1.0.0'
__date__ = '2017-08-27'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import os
from ftplib import FTP


class Connect(object):

    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

    def command_ls(self, path):
        ftp = FTP()
        ftp.connect(self.ip, self.port)
        ftp.login(self.username, self.password)
        try:
            data = []
            content = ''
            ftp.dir(path, data.append)
            dirname = os.path.dirname(path)
            catalog = ftp.nlst(dirname)
            if path != '/' and catalog.count(path) == 0:
                print('no such directory! ')
            else:
                for line in data:
                    content += (line+'\n')
                return content[:-1]
        except Exception:
            print('retrieve content failure! ')
        finally:
            ftp.quit()

    def command_mkdir(self, path):
        ftp = FTP()
        ftp.connect(self.ip, self.port)
        ftp.login(self.username, self.password)
        try:
            ftp.mkd(path)
        except Exception:
            print('create directory failure! ')
        else:
            print('create directory success! ')
        finally:
            ftp.quit()

    def ftp_put(self, localfile, remotefile):
        ftp = FTP()
        ftp.connect(self.ip, self.port)
        ftp.login(self.username, self.password)

        def list_put(localstuff, remotestuff):
            dirname = os.path.dirname(remotestuff)
            if ftp.nlst(dirname).count(remotestuff) == 0:
                ftp.mkd(remotestuff)
            for content in os.listdir(localstuff):
                localpath = localstuff + os.sep + content
                remotepath = remotestuff + '/' + content
                if os.path.isfile(localpath):
                    handler = open(localpath, 'rb')
                    ftp.storbinary('STOR %s' % remotepath, handler)
                    handler.close()
                else:
                    list_put(localpath, remotepath)
        try:
            if os.path.isfile(localfile):
                handle = open(localfile, 'rb')
                ftp.storbinary('STOR %s' % remotefile, handle)
                handle.close()
            else:
                list_put(localfile, remotefile)
        except Exception:
            print('upload file failure! ')
        finally:
            ftp.quit()

    def ftp_get(self, remotefile, localfile):
        ftp = FTP()
        ftp.connect(self.ip, self.port)
        ftp.login(self.username, self.password)

        def list_get(remotestuff, localstuff):
            if os.path.isdir(localstuff) is False:
                os.mkdir(localstuff)
            for index, content in enumerate(ftp.nlst(remotestuff)):
                data = []
                ftp.dir(remotestuff, data.append)
                remotepath = content
                localpath = localstuff + os.sep + os.path.basename(content)
                if data[index].startswith('-'):
                    handler = open(localpath, 'wb').write
                    ftp.retrbinary('RETR %s' % remotepath, handler)
                    handler.close()
                else:
                    list_get(remotepath, localpath)
        try:
            lists = []
            item = ''
            dirname = os.path.dirname(remotefile)
            basename = os.path.basename(remotefile)
            ftp.dir(dirname, lists.append)
            for value in lists:
                if value.endswith(basename):
                    item = value
            if item.startswith('-'):
                handle = open(localfile, 'wb').write
                ftp.retrbinary('RETR %s' % remotefile, handle)
                handle.close()
            else:
                list_get(remotefile, localfile)
        except Exception:
            print('download file failure! ')
        finally:
            ftp.quit()

