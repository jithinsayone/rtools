#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'arvin'

import requests
import base64
from requests.auth import HTTPBasicAuth
from base_upgrade import BaseUpgrader
from ...http_helper import ErrorTimeout
from ...http_helper import HttpHelper


class Upgrader(BaseUpgrader):
    """"""

    def __init__(self, addr, port, username, passwd, session, firmware, debug=False):
        BaseUpgrader.__init__(self, addr, port, username, passwd, session, firmware, debug)
        auth_cookie = base64.b64encode(self.username + ':' + self.password)
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
        self.headers['Accept-Language'] = 'en-US',
        self.headers['Referer'] = '',
        self.headers['Cookie'] = 'tLargeScreenP=1; subType=pcSub; Authorization=Basic ' + auth_cookie

        self.base_url = self.addr + ':' + str(self.port)
        self.post_url = self.base_url + '/incoming/Firmware.htm'
        self.upgrade_url = self.base_url + '/userRpm/FirmwareUpdateTemp.htm'

    def upgrade(self):
        try:
            self.post_file(self.post_url, self.firmware, 3)
        except requests.RequestException:
            self.print_with_lock(self.addr + ': send firmware failed')
            return

        try:
            self.headers['Referer'] = self.post_url
            r = HttpHelper.connect_auth_with_headers(None, self.upgrade_url, 3, (self.username, self.password),
                                                     self.headers)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': send upgrade instruction failed')
        else:
            self.print_with_lock(self.addr + ': success')

    def post_file(self, url, filename_path, times):
        self.headers['Referer'] = self.base_url + '/userRpm/SoftwareUpgradeRpm.htm'
        multiple_files = [('Filename', open(filename_path, 'rb'))]
        for x in xrange(times):
            try:
                r = requests.post(url, file=multiple_files, auth=HTTPBasicAuth(self.username, self.password))
                return
            except requests.RequestException:
                pass
        raise requests.RequestException
