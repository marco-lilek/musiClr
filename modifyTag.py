import taglib
import os

TEMP_FILENAME = "temp.mp3"

class TagWrapper:
   def __init__(self, fileName):
      self.fileName = fileName
      try:
         self.tag = taglib.MP3(fileName)
      except:
         self.tag = None

   def __enter__(self):
      return self
   
   def __exit__(self, type, value, traceback):
      if self.tag != None:
         del self.tag
      
   def hasTags(self):
      return self.tag.artist is not None and self.tag.name is not None

   def getData(self):
      return self.tag.artist, self.tag.name

   def modify(self, artist, name):
      if self.tag == None:
         raise TypeError
      self.tag.artist = artist
      self.tag.name = name
      self.tag.dump(TEMP_FILENAME)
      del self.tag
      self.tag = None
      os.remove(self.fileName)
      os.rename(TEMP_FILENAME, self.fileName)
