import cPickle as pickle
import os

# For permanant data
class Storage:
   def __init__(self):
      pass
   
   def __enter__(self):
      try:
         self.file = open("sav", "rb")
         self.data = pickle.load(self.file)
         self.file.close()
      except:
         self.data = {
            "artists": set(),
            "settings": {
               "useLastFM": True, 
               "overwriteTags": False
            },
            "targetDir": "C:\\"
         }
      return self
   def __exit__(self, arg1, arg2, arg3):
      self.file = open("sav", "wb")
      pickle.dump(self.data, self.file)
      self.file.close()
