import wx
import storage
import processor

from glob import glob
import os
from os.path import join
import taglib
import mp3parser

# Helper fxn for the process
import ntpath
def pathLeaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

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
        try:
            self.resultsWindow.Close()
        except:
            # If the window doesn't exist or if has already been closed
            pass

        # Update the target dir
        self.storage.data["targetDir"] = self.dirSelect.GetValue()

        # Get all files in desired dir
        files = glob(join(self.storage.data["targetDir"], "*.mp3"))

        dlg = wx.ProgressDialog(
            "Running",
            "Current Song: ",
            maximum = len(files) + 1,
            parent=self,
            style = 0
            | wx.PD_APP_MODAL
            | wx.PD_CAN_ABORT
            | wx.PD_ELAPSED_TIME
            | wx.PD_ESTIMATED_TIME
            | wx.PD_REMAINING_TIME)

        # Update the artist list
        mp3parser.artistList = self.storage.data["artists"]
        
        finished = 0
        results = []
        for fileName in files:
            finished += 1
            raw = pathLeaf(fileName)[:-4]
            keepgoing, skip = dlg.Update(finished, "Current Song: " + raw)
            if not keepgoing:
                break

            try:
                tag = taglib.MP3(fileName)
            except:
                results.append(["Error", raw, "", ""])
                continue

            # TODO: Maybe add option to overwrite old data
            if not self.storage.data["settings"]["overwriteTags"] and tag.artist is not None and tag.name is not None:
                mp3parser.artistList.add(tag.artist.lower())
                results.append(["Skipped", raw, tag.artist, tag.name])
                del tag
                continue

            artist, name = mp3parser.parse(raw, self.storage.data["settings"]["useLastFM"])
            if artist is None:
                results.append(["Bad", raw, "", ""])
                del tag
            else:
                tag.artist = artist
                tag.name = name
                tag.dump("temp.mp3")
                del tag
                os.remove(fileName)
                os.rename("temp.mp3", fileName)

                results.append(["Good", raw, artist, name])

        self.storage.data["artists"] = mp3parser.artistList
        dlg.Destroy()

        # Create the new window then show the results
        self.resultsWindow = wx.Frame(self, -1, title="Results",
                     pos=(100,100), size=(800,400), style=wx.DEFAULT_FRAME_STYLE)
        pr = processor.ProcessPanel(self.resultsWindow, results, files)
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
        Window(None, -1, title="mp3 cleaner - Marco Lilek", storage=s)
        app.MainLoop()
    
