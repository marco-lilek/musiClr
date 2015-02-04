import wx
import wx.dataview as dv
import storage
import taglib
import os

# TODO: Rename the panel to results

class SongListModel(dv.PyDataViewIndexListModel):
    def __init__(self, data, fileSources):
        dv.PyDataViewIndexListModel.__init__(self, len(data))
        self.data = data
        self.fileSources = fileSources

    def GetColumnType(self, col):
        return "string"

    def GetValueByRow(self, row, col):
        return self.data[row][col]

    def SetValueByRow(self, value, row, col):
        if col == 1:
            return

        changed = False
        try:
            tag = taglib.MP3(self.fileSources[row])
            if col == 2:
                if tag.artist != value:
                    changed = True
                tag.artist = value
            else:
                if tag.name != value:
                    changed = True
                tag.name = value

            if changed: 
                tag.dump("temp.mp3")
                del tag
                os.remove(self.fileSources[row])
                os.rename("temp.mp3", self.fileSources[row])
                self.data[row][col] = value
            else:
                del tag
        except:
            print "error editing tags"
    
    def GetColumnCount(self):
        return len(self.data[0])

    def GetCount(self):
        return len(self.data)

    def GetAttrByRow(self, row, col, attr):
        # TODO: for success/failure
        if col == 0:
            if self.data[row][col] == "Good":
                attr.SetColour('dark green')
            elif self.data[row][col] == "Bad" or self.data[row][col] == "Error":
                attr.SetColour('red')
            else:
                attr.SetColour('blue')
            attr.SetBold(True)
            return True
        return False

    def AddRow(self, value):
        # update data structure
        self.data.append(value)
        # notify views
        self.RowAppended()

class ProcessPanel(wx.Panel):
    def __init__(self, parent, data, fileSources):
        wx.Panel.__init__(self, parent, -1)
        
        # Permanent info
        self.dvc = dv.DataViewCtrl(self,
                                   style=wx.BORDER_THEME
                                   | dv.DV_ROW_LINES
                                   | dv.DV_VERT_RULES
                                   | dv.DV_MULTIPLE)
        self.data = data
        self.model = SongListModel(self.data, fileSources)
        self.dvc.AssociateModel(self.model)

        self.dvc.AppendTextColumn("Source", 1, width=300, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Artist", 2, width=200, mode=dv.DATAVIEW_CELL_EDITABLE)
        self.dvc.AppendTextColumn("Title", 3, width=220, mode=dv.DATAVIEW_CELL_EDITABLE)
        idCol = self.dvc.PrependTextColumn("Result", 0, width=60)
        idCol.MinWidth = 60

        self.Sizer = wx.BoxSizer(wx.VERTICAL) 
        self.Sizer.Add(self.dvc, 1, wx.EXPAND)