
import sys
import os

import httplib
import time
import socket
import struct
import binascii
from proxy_dir import current_path

import OpenSSL
SSLError = OpenSSL.SSL.WantReadError

import socks
import check_local_network
from config import config
import cert_util
from openssl_wrap import SSLConnection

from xlog import getLogger
xlog = getLogger("gae_proxy")


g_cacertfile = os.path.join(current_path, "cacert.pem")
openssl_context = SSLConnection.context_builder(ca_certs=g_cacertfile)
openssl_context.set_session_id(binascii.b2a_hex(os.urandom(10)))
if hasattr(OpenSSL.SSL, 'SESS_CACHE_BOTH'):
    openssl_context.set_session_cache_mode(OpenSSL.SSL.SESS_CACHE_BOTH)

max_timeout = 5

default_socket = socket.socket


def load_proxy_config():
    global default_socket
    if config.PROXY_ENABLE:

        if config.PROXY_TYPE == "HTTP":
            proxy_type = socks.HTTP
        elif config.PROXY_TYPE == "SOCKS4":
            proxy_type = socks.SOCKS4
        elif config.PROXY_TYPE == "SOCKS5":
            proxy_type = socks.SOCKS5
        else:
            xlog.error("proxy type %s unknown, disable proxy", config.PROXY_TYPE)
            raise

        socks.set_default_proxy(proxy_type, config.PROXY_HOST, config.PROXY_PORT, config.PROXY_USER, config.PROXY_PASSWD)
load_proxy_config()


def connect_ssl(ip, port=443, timeout=5, openssl_context=None, check_cert=True):
    ip_port = (ip, port)

    if not openssl_context:
        openssl_context = SSLConnection.context_builder()

    if config.PROXY_ENABLE:
        sock = socks.socksocket(socket.AF_INET)
    else:
        sock = socket.socket(socket.AF_INET)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # set struct linger{l_onoff=1,l_linger=0} to avoid 10048 socket error
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
    # resize socket recv buffer 8K->32K to improve browser releated application performance
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 32*1024)
    sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, True)
    sock.settimeout(timeout)

    ssl_sock = SSLConnection(openssl_context, sock, ip)
    ssl_sock.set_connect_state()

    time_begin = time.time()
    ssl_sock.connect(ip_port)
    time_connected = time.time()
    ssl_sock.do_handshake()
    time_handshaked = time.time()

    # report network ok
    check_local_network.network_stat = "OK"
    check_local_network.last_check_time = time_handshaked
    check_local_network.continue_fail_count = 0

    cert = ssl_sock.get_peer_certificate()
    if not cert:
        raise socket.error(' certficate is none')

    if check_cert:
        issuer_commonname = next((v for k, v in cert.get_issuer().get_components() if k == 'CN'), '')
        if not issuer_commonname.startswith('Google'):
            raise socket.error(' certficate is issued by %r, not Google' % ( issuer_commonname))

    connct_time = int((time_connected - time_begin) * 1000)
    handshake_time = int((time_handshaked - time_connected) * 1000)
    #xlog.debug("conn: %d  handshake:%d", connct_time, handshake_time)

    # sometimes, we want to use raw tcp socket directly(select/epoll), so setattr it to ssl socket.
    ssl_sock._sock = sock
    ssl_sock.connct_time = connct_time
    ssl_sock.handshake_time = handshake_time

    return ssl_sock


def get_ssl_cert_domain(ssl_sock):
    cert = ssl_sock.get_peer_certificate()
    if not cert:
        raise SSLError("no cert")

    #issuer_commonname = next((v for k, v in cert.get_issuer().get_components() if k == 'CN'), '')
    ssl_cert = cert_util.SSLCert(cert)
    ssl_sock.domain = ssl_cert.cn


def check_goagent(ssl_sock, appid):
    request_data = 'GET /_gh/ HTTP/1.1\r\nHost: %s.appspot.com\r\n\r\n' % appid
    ssl_sock.send(request_data.encode())
    response = httplib.HTTPResponse(ssl_sock, buffering=True)

    response.begin()
    if response.status == 404:
        return False

    if response.status == 503:
        # out of quota
        server_type = response.getheader('Server', "")
        if "gws" not in server_type and "Google Frontend" not in server_type and "GFE" not in server_type:
            return False
        else:
            return True

    if response.status != 200:
        return False

    content = response.read()
    if "GoAgent" not in content:
        return False

    return True


# export api for google_ip, appid_manager
def test_gae_ip(ip, appid=None):
    try:
        ssl_sock = connect_ssl(ip, timeout=max_timeout, openssl_context=openssl_context)
        get_ssl_cert_domain(ssl_sock)

        if not appid:
            appid = "xxnet-1"
        if not check_goagent(ssl_sock, appid):
            return False

        return ssl_sock
    except socket.timeout:
        return False
    except Exception as e:
        return False
