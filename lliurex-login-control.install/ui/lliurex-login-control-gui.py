#!/usr/bin/python3

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine

import sys
import LliurexLoginControl

app = QApplication()
app.setDesktopFileName("lliurex-login-control")
engine = QQmlApplicationEngine()
engine.clearComponentCache()
context=engine.rootContext()
loginControlBridge=LliurexLoginControl.LliurexLoginControl(sys.argv[1])
context.setContextProperty("loginControlBridge", loginControlBridge)

url = QUrl("/usr/share/lliurex-login-control/rsrc/lliurex-login-control.qml")

engine.load(url)
if not engine.rootObjects():
	sys.exit(-1)

engine.quit.connect(app.quit)
ret=app.exec()
del engine
del app
sys.exit(ret)

