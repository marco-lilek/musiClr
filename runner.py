import os
import ntpath
from glob import glob
from os.path import join
import mp3parser
import taglib

def pathLeaf(path):
   head, tail = ntpath.split(path)
   return tail or ntpath.basename(head)

class Runner():
   def __init__(self, configs):
      # We do this here to make it clear what data we need
      self.targetDir = configs['targetDir']
      self.artistList = configs['artists']
      self.useLastFm = configs['settings']['useLastFM']
      self.overwriteTags = configs['settings']['overwriteTags']

      self.files = glob(join(self.targetDir, "*.mp3"))
      self.results = []
      
   def run(self, dlg):
      # They now share the same information
      mp3parser.artistList = self.artistList
      
      finished = 0
      for fileName in self.files:
         finished += 1
         raw = pathLeaf(fileName)[:-4]
         
         dlg.Update(finished, "Current Song: " + raw)

         try:
            tag = taglib.MP3(fileName)
         except:
            self.results.append(["Error", raw, "", ""])

         if not self.overwriteTags and tag.artist is not None and tag.name is not None:
            mp3parser.addToArtistList(tag.artist)
            self.results.append(["Skipped", raw, tag.artist, tag.name])
            del tag
            continue

         artist, name = mp3parser.parse(raw, self.useLastFm)

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

      self.artistList = mp3parser.artistList
