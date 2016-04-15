#!/usr/bin/env python3
# coding:utf-8
# Based on GAppProxy 2.0.0 by Du XiaoGang <dugang.2008@gmail.com>
# Based on WallProxy 0.4.0 by Hust Moon <www.ehust@gmail.com>
# Contributor:
#      Phus Lu           <phus.lu@gmail.com>
#      Hewig Xu          <hewigovens@gmail.com>
#      Ayanamist Yang    <ayanamist@gmail.com>
#      V.E.O             <V.E.O@tom.com>
#      Max Lv            <max.c.lv@gmail.com>
#      AlsoTang          <alsotang@gmail.com>
#      Christopher Meng  <cickumqt@gmail.com>
#      Yonsm Guo         <YonsmGuo@gmail.com>
#      Parkman           <cseparkman@gmail.com>
#      Ming Bai          <mbbill@gmail.com>
#      Bin Yu            <yubinlove1991@gmail.com>
#      lileixuan         <lileixuan@gmail.com>
#      Cong Ding         <cong@cding.org>
#      Zhang Youfu       <zhangyoufu@gmail.com>
#      Lu Wei            <luwei@barfoo>
#      Harmony Meow      <harmony.meow@gmail.com>
#      logostream        <logostream@gmail.com>
#      Rui Wang          <isnowfy@gmail.com>
#      Wang Wei Qiang    <wwqgtxx@gmail.com>
#      Felix Yan         <felixonmars@gmail.com>
#      QXO               <qxodream@gmail.com>
#      Geek An           <geekan@foxmail.com>
#      Poly Rabbit       <mcx_221@foxmail.com>
#      oxnz              <yunxinyi@gmail.com>
#      Shusen Liu        <liushusen.smart@gmail.com>
#      Yad Smood         <y.s.inside@gmail.com>
#      Chen Shuang       <cs0x7f@gmail.com>
#      cnfuyu            <cnfuyu@gmail.com>
#      cuixin            <steven.cuixin@gmail.com>

__version__ = '1.1'

import sys
import os

sys.dont_write_bytecode = True

__file__ = os.path.abspath(__file__)
if os.path.islink(__file__):
    __file__ = getattr(os, 'readlink', lambda x: x)(__file__)
work_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(work_path)
data_path = os.path.join(work_path, 'data')
if not os.path.isdir(data_path): os.mkdir(data_path)

# add python lib path
sys.path.append(os.path.join(work_path, 'pythonlib'))
if sys.platform.startswith("linux"):
    sys.path.append(os.path.join(work_path, 'pythonlib.egg'))
    # reduce resource request for threading, for OpenWrt
    import threading
    threading.stack_size(128*1024)
elif sys.platform == "darwin":
    sys.path.append(os.path.join(work_path, 'pythonlib.egg'))


from local.config import config
from OpenSSL import version as openssl_version

from xlog import getLogger
xlog = getLogger("gae_proxy")
xlog.set_buffer(500)
if config.log_file:
    log_file = os.path.join(data_gae_proxy_path, "local.log")
    xlog.set_file(log_file)


def summary():
    appids = '|'.join(config.GAE_APPIDS) if config.GAE_APPIDS else 'Using Public APPID'
    if len(appids) > 56:
        appids = appids[:55] + '..'

    pac_ip = config.PAC_IP
    if config.PAC_IP != '127.0.0.1':
        pac_ip = config.get_listen_ip()

    info  = '-'*80
    info += '\nXX-Mini Version     : %s (python/%s pyopenssl/%s)\n' % (__version__, sys.version.split()[0], openssl_version.__version__)
    info += 'Listen Address      : %s:%d\n' % (config.LISTEN_IP if config.LISTEN_IP == '127.0.0.1' else config.get_listen_ip(), config.LISTEN_PORT)
    info += 'Setting File        : %sproxy.ini\n' % (config.MANUAL_LOADED + '/' if config.MANUAL_LOADED else '')
    info += '%s Proxy %s : %s:%s\n' % (config.PROXY_TYPE, ' '*(12-len(config.PROXY_TYPE)), config.PROXY_HOST, config.PROXY_PORT) if config.PROXY_ENABLE else ''
    info += 'GAE APPID           : %s\n' % appids
    info += 'Pac Server          : http://%s:%d/%s\n' % (pac_ip, config.PAC_PORT, config.PAC_FILE) if config.PAC_ENABLE else ''
    info += 'CA File             : http://%s:%d/%s\n' % (pac_ip, config.PAC_PORT, 'CA.crt') if config.PAC_ENABLE else ''
    info += 'Pac File            : file://%s\n' % os.path.abspath(os.path.join(data_path, config.PAC_FILE)) if config.PAC_ENABLE else ''
    info += '-'*80
    return info

xlog.info(summary())
xlog.set_time()
if config.LISTEN_DEBUGINFO:
    xlog.set_debug()

import time
import random
import threading
import urllib.request, urllib.error, urllib.parse

import simple_http_server
from local import proxy_handler
from local import connect_control
from local import connect_manager
from local.cert_util import CertUtil
from local.gae_handler import spawn_later
from local.pac_server import PACServerHandler


def pre_start():

    def get_windows_running_process_list():
        import os
        import glob
        import ctypes
        import collections
        Process = collections.namedtuple('Process', 'pid name exe')
        process_list = []
        if os.name == 'nt':
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010
            lpidProcess= (ctypes.c_ulong * 1024)()
            cb = ctypes.sizeof(lpidProcess)
            cbNeeded = ctypes.c_ulong()
            ctypes.windll.psapi.EnumProcesses(ctypes.byref(lpidProcess), cb, ctypes.byref(cbNeeded))
            nReturned = cbNeeded.value/ctypes.sizeof(ctypes.c_ulong())
            pidProcess = [i for i in lpidProcess][:nReturned]
            has_queryimage = hasattr(ctypes.windll.kernel32, 'QueryFullProcessImageNameA')
            for pid in pidProcess:
                hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, 0, pid)
                if hProcess:
                    modname = ctypes.create_string_buffer(2048)
                    count = ctypes.c_ulong(ctypes.sizeof(modname))
                    if has_queryimage:
                        ctypes.windll.kernel32.QueryFullProcessImageNameA(hProcess, 0, ctypes.byref(modname), ctypes.byref(count))
                    else:
                        ctypes.windll.psapi.GetModuleFileNameExA(hProcess, 0, ctypes.byref(modname), ctypes.byref(count))
                    exe = modname.value
                    name = os.path.basename(exe)
                    process_list.append(Process(pid=pid, name=name, exe=exe))
                    ctypes.windll.kernel32.CloseHandle(hProcess)
        elif sys.platform.startswith('linux'):
            for filename in glob.glob('/proc/[0-9]*/cmdline'):
                pid = int(filename.split('/')[2])
                exe_link = '/proc/%d/exe' % pid
                if os.path.exists(exe_link):
                    exe = os.readlink(exe_link)
                    name = os.path.basename(exe)
                    process_list.append(Process(pid=pid, name=name, exe=exe))
        else:
            try:
                import psutil
                process_list = psutil.get_process_list()
            except Exception as e:
                xlog.exception('psutil.get_windows_running_process_list() failed: %r', e)
        return process_list


    if sys.platform == 'cygwin':
        xlog.info('cygwin is not officially supported, please continue at your own risk :)')
        #sys.exit(-1)
    elif os.name == 'posix':
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_NOFILE, (8192, -1))
        except Exception as e:
            pass
    elif os.name == 'nt':
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW('XX-Mini v%s' % __version__)
        if not config.LISTEN_VISIBLE:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        else:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
        if config.LOVE_ENABLE and random.randint(1, 100) <= 20:
            title = ctypes.create_unicode_buffer(1024)
            ctypes.windll.kernel32.GetConsoleTitleW(ctypes.byref(title), len(title)-1)
            ctypes.windll.kernel32.SetConsoleTitleW('%s %s' % (title.value, random.choice(config.LOVE_TIP)))
        blacklist = {'360safe': False,
                     'QQProtect': False, }
        softwares = [k for k, v in blacklist.items() if v]
        if softwares:
            tasklist = '\n'.join(x.name for x in get_windows_running_process_list()).lower()
            softwares = [x for x in softwares if x.lower() in tasklist]
            if softwares:
                title = 'XX-Mini 建议'
                error = '某些安全软件(如 %s)可能和本软件存在冲突，造成 CPU 占用过高。\n如有此现象建议暂时退出此安全软件来继续运行XX-Mini' % ','.join(softwares)
                ctypes.windll.user32.MessageBoxW(None, error, title, 0)
                #sys.exit(0)
    if config.PAC_ENABLE:
        pac_ip = config.PAC_IP
        url = 'http://%s:%d/%s' % (pac_ip, config.PAC_PORT, config.PAC_FILE)
        spawn_later(600, urllib.request.build_opener(urllib.request.ProxyHandler({})).open, url)


def main():
    pre_start()

    connect_control.keep_running = True
    connect_manager.https_manager.load_config()
    xlog.debug("## GAEProxy set keep_running: %s", connect_control.keep_running)

    CertUtil.init_ca()

    proxy_daemon = simple_http_server.HTTPServer((config.LISTEN_IP, config.LISTEN_PORT), proxy_handler.GAEProxyHandler)
    proxy_thread = threading.Thread(target=proxy_daemon.serve_forever)
    proxy_thread.setDaemon(True)
    proxy_thread.start()

    if config.PAC_ENABLE:
        pac_daemon = simple_http_server.HTTPServer((config.PAC_IP, config.PAC_PORT), PACServerHandler)
        pac_thread = threading.Thread(target=pac_daemon.serve_forever)
        pac_thread.setDaemon(True)
        pac_thread.start()
        try:
            urllib.request.urlopen('http://127.0.0.1:%d/%s' % (config.PAC_PORT, config.PAC_FILE))
        except:
            pass

    while connect_control.keep_running:
        time.sleep(1)

    proxy_daemon.shutdown()
    proxy_daemon.server_close()
    proxy_thread.join()
    if config.PAC_ENABLE:
        pac_daemon.shutdown()
        pac_daemon.server_close()
        pac_thread.join()


def terminate():
    xlog.info("start to terminate GAE_Proxy")
    connect_control.keep_running = False
    xlog.debug("## Set keep_running: %s", connect_control.keep_running)
    sys.exit()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        terminate()
