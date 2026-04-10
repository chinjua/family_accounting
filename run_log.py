# -*- coding: utf-8 -*-
import sys
import traceback
import os
import time

os.environ['PYTHONIOENCODING'] = 'utf-8'

log_file = open('D:/family_accounting/error.log', 'w', encoding='utf-8')

def log(msg):
    log_file.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")
    log_file.flush()
    print(f"{time.strftime('%H:%M:%S')} - {msg}")

log("Starting app...")

try:
    import wx
    log("wx imported")
    
    # 设置全局异常处理
    def exception_hook(exc_type, exc_value, exc_traceback):
        log(f"EXCEPTION: {exc_type.__name__}: {exc_value}")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=log_file)
        log_file.flush()
    
    sys.excepthook = exception_hook
    
    from login import LoginDialog
    log("LoginDialog imported")
    
    app = wx.App()
    log("App created")
    
    login_dlg = LoginDialog()
    log("LoginDialog created, about to ShowModal")
    
    result = login_dlg.ShowModal()
    log(f"Login result: {result}")
    
    if result == wx.ID_OK:
        user = login_dlg.get_user()
        login_dlg.Destroy()
        log(f"User: {user}")
        
        if user:
            from main_frame import MainFrame
            log("MainFrame imported")
            frame = MainFrame(user)
            log("MainFrame created")
            frame.Show()
            log("MainFrame shown")
            app.MainLoop()
            log("MainLoop exited")
    else:
        login_dlg.Destroy()
        
except Exception as e:
    log(f"ERROR: {e}")
    traceback.print_exc(file=log_file)
    log_file.flush()

log("Program ended")
log_file.close()
