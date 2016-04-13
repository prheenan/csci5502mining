from __future__ import division
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.naive_bayes import GaussianNB

import Learner

class LogisticLearner(Learner.Learner):
	def __init__(self, FeatureMask):
		super(LogisticLearner, self).__init__(FeatureMask)
		self.arr = np.hstack([FeatureMask.ForceStd.reshape(-1,1), FeatureMask.ForceMinMax.reshape(-1,1)])
		self.expected = FeatureMask.LabelsForAllPoints

	def FitAndPredict(self):
		test = self.GaussNB()
		# testExp = 
		model = LogisticRegression(solver='sag', C=5)
		model = model.fit(test, self.expected)
		return model.predict(self.arr)

	def GaussNB(self):
		model = GaussianNB()
		model.fit(self.arr, self.expected)
		print model.predict(self.arr).shape
		return model.predict(self.arr).reshape(-1,1)
