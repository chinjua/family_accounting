# -*- coding: utf-8 -*-
"""
家庭记账软件 - 入口文件
"""
import wx
from login import LoginDialog
from main_frame import MainFrame


def main():
    """主函数"""
    app = wx.App()
    
    while True:
        login_dlg = LoginDialog()
        result = login_dlg.ShowModal()
        
        if result == wx.ID_OK:
            user = login_dlg.get_user()
            login_dlg.Destroy()
            
            if user:
                frame = MainFrame(user)
                frame.Show()
                app.MainLoop()
                break
            else:
                break
        else:
            login_dlg.Destroy()
            break


if __name__ == "__main__":
    main()
