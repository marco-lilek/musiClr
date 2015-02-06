import wx
from runner import Runner
from results import ResultsWindow

class MainWindow(wx.Frame):
   def __init__(self, storage):
      wx.Frame.__init__(self, None, -1, "musiClr", (100,100), (300,275), wx.DEFAULT_FRAME_STYLE)
      # Close
      self.resultsWindow = None
      self.storage = storage
      self.Bind(wx.EVT_CLOSE, self.onClose)
      
      panel = wx.Panel(self, -1)

      # Elements
      text = wx.StaticText(panel, -1, label="Process songs in the selected dir",
                    style=wx.ALIGN_CENTER)
      
      settingsButton = wx.Button(panel, -1, "Settings")
      panel.Bind(wx.EVT_BUTTON, self.EvtSettings, settingsButton)
      
      runButton = wx.Button(panel, -1, "Run Script")
      panel.Bind(wx.EVT_BUTTON, self.EvtRun, runButton)
      
      # Dir
      dirSelect = wx.TextCtrl(panel, -1, self.storage.data["targetDir"])
      self.dirSelect = dirSelect
      dirSelect.SetInsertionPoint(0)
      panel.Bind(wx.EVT_TEXT, self.EvtText, dirSelect)
      
      pickDir = wx.Button(panel, -1, "Select dir to process")
      panel.Bind(wx.EVT_BUTTON, self.PickDir, pickDir)
      
      # Hold the elements
      sizer = wx.BoxSizer(wx.VERTICAL)
      sizer.Add(text, 0, wx.EXPAND | wx.ALL, 10)

      # Controls
      box = wx.StaticBox(panel, -1, "", style=wx.ALIGN_CENTER)
      bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
      bsizer.Add(settingsButton, 0, wx.EXPAND | wx.ALL, 5)
      bsizer.Add(runButton, 0, wx.EXPAND | wx.ALL, 5)

      sizer.Add(pickDir, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)
      sizer.Add(dirSelect, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
      
      sizer.Add(bsizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
      sizer.SetSizeHints(panel)
      panel.SetSizer(sizer)
      
      self.Show()
      
   def onClose(self, event):
      self.Destroy()

   def EvtSettings(self, event):
      settings = self.storage.data["settings"]
      keyList = list(settings)
      selected = list([i for i,k in enumerate(keyList) if settings[k] == True])

      dlg = wx.MultiChoiceDialog( self, "Select desired settings", "Settings", keyList)
      dlg.SetSelections(selected)

      if (dlg.ShowModal() == wx.ID_OK):
         selections = dlg.GetSelections()
         for k in keyList:
            settings[k] = False
         for ind in selections:
            settings[keyList[ind]] = True
      dlg.Destroy()

   def EvtText(self, event):
      self.storage.data["targetDir"] = event.GetString()

   def EvtRun(self, event):
      runner = Runner(self.storage.data)

      dlg = wx.ProgressDialog(
         "Running",
         "Current Song: ",
         maximum = len(runner.files) + 1,
         parent=self,
         style = 0
         | wx.PD_APP_MODAL
         | wx.PD_CAN_ABORT
         | wx.PD_ELAPSED_TIME
         | wx.PD_ESTIMATED_TIME
         | wx.PD_REMAINING_TIME)
      
      runner.run(dlg)
      dlg.Destroy()

      self.resultsWindow = ResultsWindow(self, runner.results, self.storage.data["targetDir"])

   def PickDir(self, event):
      dlg = wx.DirDialog(
         self, "Choose a directory:",
         style=wx.DD_DEFAULT_STYLE
            | wx.DD_DIR_MUST_EXIST)
      if dlg.ShowModal() == wx.ID_OK:
         self.dirSelect.Clear()
         result = dlg.GetPath()
         self.dirSelect.ChangeValue(result)
         self.EvtText(result)
      dlg.Destroy()