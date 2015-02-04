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
            print "good"
            print self.data
        except:
            self.data = {"artists":set(),
                         "settings":{"useLastFM":True, "overwriteTags":False},
                         "targetDir":"C:\\"}
        return self
    def __exit__(self, arg1, arg2, arg3):
        print self.data
        self.file = open("sav", "wb")
        pickle.dump(self.data, self.file)
        self.file.close()

    # Artists
    # self.data["artists"]

    # Use last FM
    # self.data["settings"]
    
    # target directory
    # self.data["targetDir"]
    