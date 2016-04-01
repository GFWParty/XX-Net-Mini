#!/usr/bin/env python3
# coding:utf-8
# Contributor:
#      Phus Lu        <phus.lu@gmail.com>

__version__ = '1.6'

GOAGENT_LOGO_DATA = """\
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"""

import sys
import os
import re
import thread
import base64
import platform

try:
    import pygtk
    pygtk.require('2.0')
    import gtk
    # gtk.gdk.threads_init()
except Exception:
    sys.exit(os.system(u'gdialog --title "GoAgent GTK" --msgbox "\u8bf7\u5b89\u88c5 python-gtk2" 15 60'.encode(sys.getfilesystemencoding() or sys.getdefaultencoding(), 'replace')))
try:
    import pynotify
    pynotify.init('GoAgent Notify')
except ImportError:
    pynotify = None
try:
    import appindicator
except ImportError:
    appindicator = None
try:
    import vte
except ImportError:
    sys.exit(gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, u'请安装 python-vte').run())


def spawn_later(seconds, target, *args, **kwargs):
    def wrap(*args, **kwargs):
        import time
        time.sleep(seconds)
        return target(*args, **kwargs)
    return thread.start_new_thread(wrap, args, kwargs)


def drop_desktop():
    filename = os.path.abspath(__file__)
    dirname = os.path.dirname(filename)
    DESKTOP_FILE = '''\
#!/usr/bin/env xdg-open
[Desktop Entry]
Type=Application
Name=GoAgent GTK
Comment=GoAgent GTK Launcher
Categories=Network;Proxy;
Exec=/usr/bin/env python3 "%s"
Icon=%s/goagent-logo.png
Terminal=false
StartupNotify=true
''' % (filename, dirname)
    for dirname in map(os.path.expanduser, ['~/Desktop', u'~/桌面']):
        if os.path.isdir(dirname):
            filename = os.path.join(dirname, 'goagent-gtk.desktop')
            with open(filename, 'w') as fp:
                fp.write(DESKTOP_FILE)
            os.chmod(filename, 0755)


def should_visible():
    import ConfigParser
    ConfigParser.RawConfigParser.OPTCRE = re.compile(r'(?P<option>[^=\s][^=]*)\s*(?P<vi>[=])\s*(?P<value>.*)$')
    config = ConfigParser.ConfigParser()
    config.read(['proxy.ini', 'proxy.user.ini'])
    visible = config.has_option('listen', 'visible') and config.getint('listen', 'visible')
    return visible

#gtk.main_quit = lambda: None
#appindicator = None


class GoAgentGTK:

    command = ['/usr/bin/env', 'python3', 'proxy.py']
    message = u'GoAgent已经启动，单击托盘图标可以最小化'
    fail_message = u'GoAgent启动失败，请查看控制台窗口的错误信息。'

    def __init__(self, window, terminal):
        self.window = window
        self.window.set_size_request(652, 447)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event',self.delete_event)
        self.terminal = terminal

        for cmd in ('python3.5', 'python35', 'python3'):
            if os.system('which %s' % cmd) == 0:
                self.command[1] = cmd
                break

        self.window.add(terminal)
        self.childpid = self.terminal.fork_command(self.command[0], self.command, os.getcwd())
        if self.childpid > 0:
            self.childexited = self.terminal.connect('child-exited', self.on_child_exited)
            self.window.connect('delete-event', lambda w, e: gtk.main_quit())
        else:
            self.childexited = None

        spawn_later(0.5, self.show_startup_notify)

        if should_visible():
            self.window.show_all()

        logo_filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'goagent-logo.png')
        if not os.path.isfile(logo_filename):
            with open(logo_filename, 'wb') as fp:
                fp.write(base64.b64decode(GOAGENT_LOGO_DATA))
        self.window.set_icon_from_file(logo_filename)

        if appindicator:
            self.trayicon = appindicator.Indicator('GoAgent', 'indicator-messages', appindicator.CATEGORY_APPLICATION_STATUS)
            self.trayicon.set_status(appindicator.STATUS_ACTIVE)
            self.trayicon.set_attention_icon('indicator-messages-new')
            self.trayicon.set_icon(logo_filename)
            self.trayicon.set_menu(self.make_menu())
        else:
            self.trayicon = gtk.StatusIcon()
            self.trayicon.set_from_file(logo_filename)
            self.trayicon.connect('popup-menu', lambda i, b, t: self.make_menu().popup(None, None, gtk.status_icon_position_menu, b, t, self.trayicon))
            self.trayicon.connect('activate', self.show_hide_toggle)
            self.trayicon.set_tooltip('GoAgent')
            self.trayicon.set_visible(True)

    def make_menu(self):
        menu = gtk.Menu()
        itemlist = [(u'\u663e\u793a', self.on_show),
                    (u'\u9690\u85cf', self.on_hide),
                    (u'\u505c\u6b62', self.on_stop),
                    (u'\u91cd\u65b0\u8f7d\u5165', self.on_reload),
                    (u'\u9000\u51fa', self.on_quit)]
        for text, callback in itemlist:
            item = gtk.MenuItem(text)
            item.connect('activate', callback)
            item.show()
            menu.append(item)
        menu.show()
        return menu

    def show_notify(self, message=None, timeout=None):
        if pynotify and message:
            notification = pynotify.Notification('GoAgent Notify', message)
            notification.set_hint('x', 200)
            notification.set_hint('y', 400)
            if timeout:
                notification.set_timeout(timeout)
            notification.show()

    def show_startup_notify(self):
        if self.check_child_exists():
            self.show_notify(self.message, timeout=3)

    def check_child_exists(self):
        if self.childpid <= 0:
            return False
        cmd = 'ps -p %s' % self.childpid
        lines = os.popen(cmd).read().strip().splitlines()
        if len(lines) < 2:
            return False
        return True

    def on_child_exited(self, term):
        if self.terminal.get_child_exit_status() == 0:
            gtk.main_quit()
        else:
            self.show_notify(self.fail_message)

    def on_show(self, widget, data=None):
        self.window.show_all()
        self.window.present()
        self.terminal.feed('\r')

    def on_hide(self, widget, data=None):
        self.window.hide_all()

    def on_stop(self, widget, data=None):
        if self.childexited:
            self.terminal.disconnect(self.childexited)
        os.system('kill -9 %s' % self.childpid)

    def on_reload(self, widget, data=None):
        if self.childexited:
            self.terminal.disconnect(self.childexited)
        os.system('kill -9 %s' % self.childpid)
        self.on_show(widget, data)
        self.childpid = self.terminal.fork_command(self.command[0], self.command, os.getcwd())
        self.childexited = self.terminal.connect('child-exited', lambda term: gtk.main_quit())

    def show_hide_toggle(self, widget, data= None):
        if self.window.get_property('visible'):
            self.on_hide(widget, data)
        else:
            self.on_show(widget, data)

    def delete_event(self, widget, data=None):
        self.on_hide(widget, data)
        # 默认最小化至托盘
        return True

    def on_quit(self, widget, data=None):
        gtk.main_quit()


def main():
    global __file__
    __file__ = os.path.abspath(__file__)
    if os.path.islink(__file__):
        __file__ = getattr(os, 'readlink', lambda x: x)(__file__)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not os.path.exists('goagent-logo.png'):
        # first run and drop shortcut to desktop
        drop_desktop()

    window = gtk.Window()
    terminal = vte.Terminal()
    GoAgentGTK(window, terminal)
    gtk.main()

if __name__ == '__main__':
    main()
