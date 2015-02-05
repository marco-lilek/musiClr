import wx
import storage
import processor
from runner import Runner

from glob import glob
import os
from os.path import join



# Helper fxn for the process


class Window(wx.Frame):
    def __init__(
            self, parent, ID, title, storage, pos=(100,100),
            size=(300,275), style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
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
        self.storage.data["targetDir"] = self.dirSelect.GetValue()
        self.Destroy()
    
    def EvtSettings(self, event):
        lst = []
        selected = []
        settings = self.storage.data["settings"]
        lookup = dict(enumerate(settings))
        for ind, key in lookup.iteritems():
            lst.append(key)
            if settings[key] == True:
                selected.append(ind)

        dlg = wx.MultiChoiceDialog( self, 
                                   "Select desired settings",
                                   "Settings", lst)
        dlg.SetSelections(selected)

        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            # Reset the values
            for k in settings:
                settings[k] = False
                
            for elm in selections:
                settings[lookup[elm]] = True
        dlg.Destroy()

    def EvtText(self, event):
        self.storage.data["targetDir"] = event.GetString()

    def EvtRun(self, event):
        # Update the target dir
        self.storage.data["targetDir"] = self.dirSelect.GetValue()

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

        # Create the new window then show the results
        self.resultsWindow = wx.Frame(self, -1, title="Results",
                     pos=(100,100), size=(800,400), style=wx.DEFAULT_FRAME_STYLE)
        pr = processor.ProcessPanel(self.resultsWindow, runner.results, runner.files)
        self.resultsWindow.Show()
        
    def PickDir(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.dirSelect.Clear()
            self.dirSelect.ChangeValue(dlg.GetPath())
        dlg.Destroy()

if __name__ == "__main__":
    app = wx.App()
    with storage.Storage() as s:
        Window(None, -1, title="musiClr", storage=s)
        app.MainLoop()
    
