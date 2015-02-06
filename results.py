import wx
import wx.dataview as dv
from modifyTag import TagWrapper

NAME = "Results - "
WIDTH = 800

class ResultsWindow(wx.Frame):
   def __init__(self, parent, results, dirRun):
      print results
      toDestroy = wx.FindWindowByName(NAME)
      if not toDestroy is None:
         toDestroy.Destroy()

      wx.Frame.__init__(self, parent, -1, NAME + dirRun, (100,100), (WIDTH,400), wx.DEFAULT_FRAME_STYLE)
      panel = ResultsPanel(self, results)
      self.Show()

   def onClose(self, event):
      self.Destroy()

class ResultsPanel(wx.Panel):
   def __init__(self, parent, results):
      wx.Panel.__init__(self, parent, -1)
      
      # Permanent info
      self.dvc = dv.DataViewCtrl(
         self,
         style=wx.BORDER_THEME
            | dv.DV_ROW_LINES
            | dv.DV_VERT_RULES
            | dv.DV_MULTIPLE)
      self.model = SongListModel(results)
      self.dvc.AssociateModel(self.model)

      w1, w2, w3 = 60, 300, 200
      w4 = WIDTH - sum((w1, w2, w3, 20))  # To fill in the rest
      self.dvc.AppendTextColumn("Result", 0, width=w1).MinWidth = 60
      self.dvc.AppendTextColumn("Source", 1, width=w2, mode=dv.DATAVIEW_CELL_EDITABLE)
      self.dvc.AppendTextColumn("Artist", 2, width=w3, mode=dv.DATAVIEW_CELL_EDITABLE)
      self.dvc.AppendTextColumn("Title", 3, width=w4, mode=dv.DATAVIEW_CELL_EDITABLE)

      self.Sizer = wx.BoxSizer(wx.VERTICAL) 
      self.Sizer.Add(self.dvc, 1, wx.EXPAND)

class SongListModel(dv.PyDataViewIndexListModel):
   def __init__(self, data):
      dv.PyDataViewIndexListModel.__init__(self, len(data))
      self.data = data

   def GetColumnType(self, col):
      return "string"

   def GetValueByRow(self, row, col):
      return self.data[row][col]

   def SetValueByRow(self, value, row, col):
      if col == 1:
         return

      
      with TagWrapper(self.data[row][-1]) as tag:
         if tag.tag is None:
            return
         changed = False
         artist, name = tag.getData()
         if col == 2 and artist != value:
            artist = value
            changed = True
         elif col == 3 and name != value:
            name = value
            changed = True
         else:
            return

         if changed:
            tag.modify(artist, name)
            self.data[row][col] = value
   
   def GetColumnCount(self):
      return len(self.data[0])

   def GetCount(self):
      return len(self.data)

   def GetAttrByRow(self, row, col, attr):
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

