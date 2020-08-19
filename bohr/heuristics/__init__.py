import inspect

from snorkel.labeling import LabelingFunction

def all_lfs(module):
  lfs = [obj for name, obj in inspect.getmembers(module) 
                     if (isinstance(obj, LabelingFunction))]

  return lfs
