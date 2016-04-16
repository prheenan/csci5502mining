from __future__ import division
import sys
import numpy as np
from sklearn.neural_network import MLPClassifier
import Learner

class NeuralLearner(Learner.Learner):
	def __init__(self, FeatureMask):
		super(NeuralLearner, self).__init__(FeatureMask)
	        self.expected = FeatureMask.LabelsForAllPoints
		#self.model = MLPClassifier(algorithm='sgd', hidden_layer_sizes=(64,32))
                self.model = MLPClassifier(algorithm = 'sgd', 
                                           learning_rate = 'constant',
                                           momentum = .9,
                                           nesterovs_momentum = True, 
                                           learning_rate_init = 0.2)
        def FitAndPredict(self, mask):
                return self.Predict(self.Fit(mask))
        
        def SetupInputActivations(self, FeatureMask):
		arr = np.hstack([FeatureMask.ForceStd.reshape(-1,1), 
                                 FeatureMask.ForceMinMax.reshape(-1,1),
                                 FeatureMask.CannyFilter.reshape(-1,1)])
	        expected = FeatureMask.LabelsForAllPoints
		return arr, expected

        def Fit(self, mask):
                arr, expected = self.SetupInputActivations(mask)
                self.model.fit(arr, expected)

        def Predict(self, mask):
                arr, expected = self.SetupInputActivations(mask)
                return self.model.predict(arr).reshape(-1,1)
