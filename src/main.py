import wx
from utils.storage import Storage
from windows.mainWindow import MainWindow

if __name__ == "__main__":
   app = wx.App()
   with Storage() as s:
      MainWindow(s)
      app.MainLoop()
   
