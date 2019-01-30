# -*- coding:utf-8 -*-

# 'progressbar' documentation can be found at
# 'http://progressbar-2.readthedocs.io/en/latest/index.html'
# from progressbar import ProgressBar

# 'tqdm' comes from 'https://pypi.python.org/pypi/tqdm'
# I decided to change from 'progressbar' to 'tqdm' because it is
# compatible with jupyter notebooks
from tqdm import tqdm as ProgressBar

# This code, 'progress_timer' is a courtesy from Menno Zevenberger
# from 'https://www.themarketingtechnologist.co/progress-timer-in-python/'
#
class ProgressTimer:

    def __init__(self, n_iter, description="Something"):
        self.n_iter         = n_iter
        self.iter           = 0
        self.description    = description + ': '
        self.timer          = None
        self.initialize()

    def initialize(self):
        import progressbar as pb
        #initialize timer
        widgets = [self.description, pb.Percentage(), ' ',
                   pb.Bar(marker=pb.RotatingMarker()), ' ', pb.ETA()]
        self.timer = pb.ProgressBar(widgets=widgets, maxval=self.n_iter).start()

    def update(self, q=1):
        #update timer
        self.timer.update(self.iter)
        self.iter += q

    def finish(self):
        #end timer
        self.timer.finish()
