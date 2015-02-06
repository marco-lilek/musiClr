import ntpath
import mp3parser
from modifyTag import TagWrapper
from glob import glob
from os.path import join

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
      # They now share the same information, so we shouldn't need to reassign at the end
      mp3parser.artistList = self.artistList
      
      finished = 0
      for fileName in self.files:
         finished += 1
         raw = pathLeaf(fileName)[:-4]
         
         dlg.Update(finished, "Current Song: " + raw)
         
         with TagWrapper(fileName) as tag:
            if tag.tag is None:
               self.results.append(["Error", raw, "", "", fileName])
            elif not self.overwriteTags and tag.hasTags():
               mp3parser.addToArtistList(tag.tag.artist)
               self.results.append(["Skipped", raw, tag.tag.artist, tag.tag.name, fileName])
            else:
               artist, name = mp3parser.parse(raw, self.useLastFm)
               if artist is None:
                  self.results.append(["Bad", raw, "", "", fileName])
               else:
                  tag.modify(artist, name)
                  self.results.append(["Good", raw, artist, name, fileName])
