# -*- coding: utf-8 -*-
import sys
import traceback
import os

# 设置UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

os.chdir(r'D:\family_accounting')

try:
    import wx
    from login import LoginDialog
    
    app = wx.App()
    
    while True:
        login_dlg = LoginDialog()
        result = login_dlg.ShowModal()
        
        if result == wx.ID_OK:
            user = login_dlg.get_user()
            login_dlg.Destroy()
            
            if user:
                from main_frame import MainFrame
                frame = MainFrame(user)
                frame.Show()
                app.MainLoop()
                break
            else:
                break
        else:
            login_dlg.Destroy()
            break

except Exception as e:
    traceback.print_exc()
    input('Press Enter to exit')
