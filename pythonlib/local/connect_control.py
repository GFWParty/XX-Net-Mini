
import time
import threading
import sys

from .config import config

from xlog import getLogger
xlog = getLogger("gae_proxy")

# change to False when exit: system tray exit menu, or Ctrl+C in console
# then GoAgent will quit
# Every long running thread should check it and exit when False
# gae_proxy/local/proxy.py will check 'keep_running' continuously in a loop
# if gae_proxy wants to be up, 'keep_running' should NOT be False
keep_running = True

ccc_lock = threading.Lock()
high_prior_lock = []
low_prior_lock = []
high_prior_connecting_num = 0
low_prior_connecting_num = 0
last_connect_time = 0

# =============================================
# this design is for save resource when browser have no request for long time.
# when idle, connect pool will not maintain the connect ready link to save resources.
last_request_time = time.time()


def touch_active():
    global last_request_time
    last_request_time = time.time()


def inactive_time():
    global last_request_time
    t = time.time() - last_request_time
    return t


def is_active(timeout=60 * 30):
    if inactive_time() < timeout:
        return True
    else:
        return False
# ==============================================
# honey pot is out of date, setup in 2015-05
# The code may be deleted in the future
connect_allow_time = 0
connect_fail_time = 0
scan_allow_time = 0

block_delay = 5
scan_sleep_time = 600  # Need examination


def allow_connect():
    global connect_allow_time
    if time.time() < connect_allow_time:
        return False
    else:
        return True


def allow_scan():
    global scan_allow_time
    if not allow_connect:
        return False
    if time.time() < scan_allow_time:
        return False
    else:
        return True


def fall_into_honeypot():
    xlog.warn("fall_into_honeypot.")
    global connect_allow_time
    connect_allow_time = time.time() + block_delay


def scan_sleep():
    xlog.warn("Scan Blocked, due to exceeds Google's frequency limit. Please reduce the number of scan threads.")
    global scan_allow_time
    scan_allow_time = time.time() + scan_sleep_time
    # DOTO: Auto-reduce the setting?


def report_connect_fail():
    global connect_allow_time, connect_fail_time
    if connect_fail_time == 0:
        connect_fail_time = time.time()
    else:
        if time.time() - connect_fail_time > 60:
            connect_allow_time = time.time() + block_delay
            connect_fail_time = 0


def report_connect_success():
    global connect_fail_time
    connect_fail_time = 0


def block_stat():
    global connect_allow_time, scan_allow_time
    wait_time = connect_allow_time - time.time()
    scan_time = scan_allow_time - time.time()
    if wait_time < 0 and scan_time < 0:
        return "OK"
    elif wait_time > 0:
        return "Connect Blocked, %d seconds to wait." % wait_time
    elif scan_time > 0:
        return "Scan Blocked, %d seconds to wait." % scan_time
# =============================================
