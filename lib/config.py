#!/usr/bin/env python
# coding:utf-8


import ConfigParser
import os
import re
import io


from xlog import getLogger
xlog = getLogger("gae_proxy")
from proxy_dir import current_path



class Config(object):

    def load(self):
        """load config from proxy.ini"""
        ConfigParser.RawConfigParser.OPTCRE = re.compile(r'(?P<option>[^=\s][^=]*)\s*(?P<vi>[=])\s*(?P<value>.*)$')
        self.CONFIG = ConfigParser.ConfigParser()
        self.CONFIG_FILENAME = os.path.abspath( os.path.join(current_path, 'proxy.ini'))
        self.CONFIG.read(self.CONFIG_FILENAME)

        self.DATA_PATH = os.path.abspath( os.path.join(current_path, 'data'))
        if not os.path.isdir(self.DATA_PATH):
            self.DATA_PATH = current_path

        # load ../../../data/manual.ini, set by manual
        self.MANUAL_LOADED = False
        self.CONFIG_MANUAL_FILENAME = os.path.abspath( os.path.join(self.DATA_PATH, 'manual.ini'))
        if os.path.isfile(self.CONFIG_MANUAL_FILENAME):
            with open(self.CONFIG_MANUAL_FILENAME, 'rb') as fp:
                content = fp.read()
                try:
                    self.CONFIG.readfp(io.BytesIO(content))
                    self.MANUAL_LOADED = 'manual.ini'
                except Exception as e:
                    xlog.exception("data/manual.ini load error:%s", e)

        self.LISTEN_IP = self.CONFIG.get('listen', 'ip')
        self.LISTEN_PORT = self.CONFIG.getint('listen', 'port')
        self.LISTEN_VISIBLE = self.CONFIG.getint('listen', 'visible')
        self.LISTEN_DEBUGINFO = self.CONFIG.getint('listen', 'debuginfo')

        self.GAE_APPIDS = [x.strip() for x in self.CONFIG.get('gae', 'appid').split("|")]
        self.GAE_PASSWORD = self.CONFIG.get('gae', 'password').strip()

        fwd_endswith = []
        fwd_hosts = []
        direct_endswith = []
        direct_hosts = []
        gae_endswith = []
        gae_hosts = []
        for k, v in self.CONFIG.items('hosts'):
            if v == "fwd":
                if k.startswith('.'):
                    fwd_endswith.append(k)
                else:
                    fwd_hosts.append(k)
            elif v == "direct":
                if k.startswith('.'):
                    direct_endswith.append(k)
                else:
                    direct_hosts.append(k)
            elif v == "gae":
                if k.startswith('.'):
                    gae_endswith.append(k)
                else:
                    gae_hosts.append(k)
        self.HOSTS_FWD_ENDSWITH = tuple(fwd_endswith)
        self.HOSTS_FWD = tuple(fwd_hosts)
        self.HOSTS_GAE_ENDSWITH = tuple(gae_endswith)
        self.HOSTS_GAE = tuple(gae_hosts)
        self.HOSTS_DIRECT_ENDSWITH = tuple(direct_endswith)
        self.HOSTS_DIRECT = tuple(direct_hosts)

        self.AUTORANGE_MAXSIZE = self.CONFIG.getint('autorange', 'maxsize')
        self.AUTORANGE_WAITSIZE = self.CONFIG.getint('autorange', 'waitsize')
        self.AUTORANGE_BUFSIZE = self.CONFIG.getint('autorange', 'bufsize')
        self.AUTORANGE_THREADS = self.CONFIG.getint('autorange', 'threads')

        self.PAC_ENABLE = self.CONFIG.getint('pac', 'enable')
        self.PAC_IP = self.CONFIG.get('pac', 'ip')
        self.PAC_PORT = self.CONFIG.getint('pac', 'port')
        self.PAC_FILE = self.CONFIG.get('pac', 'file').lstrip('/')
        self.PAC_GFWLIST = self.CONFIG.get('pac', 'gfwlist')
        self.PAC_ADMODE = self.CONFIG.getint('pac', 'admode')
        self.PAC_ADBLOCK = self.CONFIG.get('pac', 'adblock') if self.PAC_ADMODE else 0
        self.PAC_EXPIRED = self.CONFIG.getint('pac', 'expired')

        self.PROXY_ENABLE = self.CONFIG.getint('proxy', 'enable')
        self.PROXY_TYPE = self.CONFIG.get('proxy', 'type')
        self.PROXY_HOST = self.CONFIG.get('proxy', 'host')
        self.PROXY_PORT = self.CONFIG.get('proxy', 'port')
        if self.PROXY_PORT == "":
            self.PROXY_PORT = 80
        else:
            self.PROXY_PORT = int(self.PROXY_PORT)
        self.PROXY_USER = self.CONFIG.get('proxy', 'user')
        self.PROXY_PASSWD = self.CONFIG.get('proxy', 'passwd')

        self.LOVE_ENABLE = self.CONFIG.getint('love', 'enable')
        self.LOVE_TIP = self.CONFIG.get('love', 'tip').encode('utf8').decode('unicode-escape').split('|')

        self.USE_IPV6 = self.CONFIG.getint('google_ip', 'use_ipv6')
        self.ip_traffic_quota = self.CONFIG.getint('google_ip', 'ip_traffic_quota')
        self.ip_traffic_quota_base = self.CONFIG.getint('google_ip', 'ip_traffic_quota_base')
        self.max_links_per_ip = self.CONFIG.getint('google_ip', 'max_links_per_ip')
        self.record_ip_history = self.CONFIG.getint('google_ip', 'record_ip_history')

        self.https_max_connect_thread = config.CONFIG.getint("connect_manager", "https_max_connect_thread")

        self.log_file = config.CONFIG.getint("system", "log_file")


        # change to True when finished import CA cert to browser
        # launcher will wait import ready then open browser to show status, check update etc
        self.cert_import_ready = False



config = Config()
config.load()
