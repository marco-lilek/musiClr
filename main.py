import wx
import storage
from mainWindow import MainWindow

if __name__ == "__main__":
   app = wx.App()
   with storage.Storage() as s:
      MainWindow(s)
      app.MainLoop()
   
