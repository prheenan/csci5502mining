# force floating point division. Can still use integer with //
from __future__ import division
# This file is used for importing the common utilities classes.
import random
import glob
import math
import os

import Learner

'''
class NetworkOpts:
    def __init__(self,precompute_distances=True,n_clusters=2,copy_x=True,
                 **kwargs):
        self.n_clusters=n_clusters
        self.copy_x =copy_x
        # any other arguments, set dynamically
        for k,v in kwargs.items():
            setattr(self,k,v)
'''

class NeuralLearner(Learner.Learner):
    def __init__(self,FeatureMask):
        super(NeuralLearner, self).__init__(FeatureMask)
        self.inputActivations = self.setupInputActivations(FeatureMask)

    def setupInputActivations(self, FeatureMask):
        inputActivations = []
        labelCounter = 0
        for SepStd, SepMinMax, ForceStd, ForceMinMax in zip(FeatureMask.SepStd,
                                                            FeatureMask.SepMinMax,
                                                            FeatureMask.ForceStd,
                                                            FeatureMask.ForceMinMax):
            inputActivations.append((([SepStd, SepMinMax, ForceStd, ForceMinMax]), self.LabelsForAllPoints[labelCounter]))
            labelCounter += 1
        return inputActivations

    def FitAndPredict(self):
        net = NeuralNetwork(self.inputActivations)
	net.makeNetwork(
                        4,  # input size
                        10, # hidden size
                        2   # output size
                       )
	if raw_input("Should I load weights? (y/n) ") == "y":
		print "loading weights...\n"
		net.loadWeights()
	else:
		print "initializing random weights...\n"
		net.initializeRandomWeights()
        if raw_input("Should I test or train? " ) == "train":
            epochs = raw_input("How many epochs should I train for? ")
            print "beginning training...\n"
	    for i in range(int(epochs)):
                    try:
                            net.train()
                    except KeyboardInterrupt:
                            break
            print "Error for latest epoch: ", net.epochError
            print "Epochs to convergence:",   net.epochs
            net.saveWeights()
            print "weights saved\n"
            return net.test()
        else:
            return net.test()

class Neuron():
	def __init__(self):
		self.act = None
		self.inputConnections  = []
		self.hiddenConnections = []
		self.outputConnections = []

class NeuralNetwork():

	def __init__(self, inputActivations):
            self.inputActivations = inputActivations
            self.inputLayer  = []
            self.hiddenLayer = []
            self.outputLayer = []
            self.epochError  = 0
            self.epochs      = 0
            self.trial       = 0

	def makeNetwork(self, input_size, hidden_size, output_size):
		for input_node in range(input_size):
			self.inputLayer.append(Neuron())
		for hidden_node in range(hidden_size):
			self.hiddenLayer.append(Neuron())
		for output_node in range(output_size):
			self.outputLayer.append(Neuron())

	def sigmoid(self,activation):
		try:
			return 1 / (1 + math.exp(-activation))
		except OverflowError:
			return 0

	def hiddenActivationFunction(self,node,index):
		xw = 0
		for input_node in self.inputLayer:
			xw += input_node.hiddenConnections[index] * float(input_node.act)
		return self.sigmoid(xw)

	def outputActivationFunction(self,node,index):
		f = 0
		for hidden_node in self.hiddenLayer:
			f += hidden_node.outputConnections[index] * float(hidden_node.act)
		return self.sigmoid(f)

	def getLabel(self,node):
		if node == self.outputLayer[0]:
			print "event detected!"
                        return 1
		elif node == self.outputLayer[1]:
			return 0

	def getExpected(self,node,timeStep):
		if timeStep[1] == 1:
			if node == self.outputLayer[0]: # first output node assigned to "event" detector
				return 1
			else:
				return 0
		elif timeStep[1] == 0:
			if node == self.outputLayer[1]: # second output node assigned to "not event" detector
				return 1
			else:
				return 0

	def trainingEpoch(self):
                print "Trial: " + str(self.trial)
		step = 0
                for timeStep in self.inputActivations:
                        if step % 10000 == 0:
                                print "Timestep:", step
			output = self.minusPhase(timeStep)
			if self.plusPhase(timeStep,output) == False:
				self.epochError += 1
                        step += 1
                self.trial += 1

	def minusPhase(self,timeStep):
                #FORWARD
		input_counter = 0
		for input_node in self.inputLayer:
			input_node.act = timeStep[0][input_counter]
			input_counter += 1
		hiddenConnection = 0
		for hidden in self.hiddenLayer:
			hidden.act = self.hiddenActivationFunction(hidden,hiddenConnection)
			hiddenConnection += 1
		outputConnection = 0
		layerActivity = []
		for output in self.outputLayer:
			output.act = self.outputActivationFunction(output,outputConnection)
			layerActivity.append((output,output.act))
			outputConnection += 1
		return max(layerActivity, key = lambda x: x[1])

	def checkMinusPhaseOutput(self,timeStep,minusPhaseOutput):
		label = self.getLabel(minusPhaseOutput[0])
		correct = False
                if timeStep[1] == 1: print "event present..."
		if timeStep[1] == label:
			correct = True
		return correct, label

	def plusPhase(self,timeStep,minusPhaseOutput):
		correct, label = self.checkMinusPhaseOutput(timeStep,minusPhaseOutput)

		#BACKWARD
		outputCounter = 0
		for output in self.outputLayer:
			error = self.getExpected(output,timeStep) - output.act
			hiddenCounter = 0
			for hidden in self.hiddenLayer:
				new_weight = (hidden.act * error) + output.hiddenConnections[hiddenCounter]
				output.hiddenConnections[hiddenCounter] = new_weight
				hidden.outputConnections[outputCounter] = new_weight
				inputCounter = 0
				for input_ in self.inputLayer:
					backprop_counter = 0
					tw = 0
					zw = 0
					for output_backprop in self.outputLayer:
						weight = output_backprop.hiddenConnections[hiddenCounter]
						tw += self.getExpected(output_backprop,timeStep) * weight
						zw += output_backprop.act * weight
						backprop_counter += 1
					new_weight = ((tw - zw) * (hidden.act * (1 - hidden.act) * input_.act)) + hidden.inputConnections[inputCounter]
					#print "EXPECTED:", self.getExpected(output,timeStep), "ACTUAL:", output.act, "OLD:", hidden.inputConnections[inputCounter], "NEW:", new_weight
					hidden.inputConnections[inputCounter] = new_weight
					input_.hiddenConnections[hiddenCounter] = new_weight
					inputCounter += 1
				hiddenCounter += 1
			outputCounter += 1
		if correct == False:
			return False
		else:
			return True

	def initializeRandomWeights(self):
		for input_node in self.inputLayer:
			for hidden_node in self.hiddenLayer:
				randomWeight = random.uniform(-1,1)
				#input_node.hiddenConnections.append((hidden_node,randomWeight))
				input_node.hiddenConnections.append(randomWeight)
				#hidden_node.inputConnections.append((input_node,randomWeight))
				hidden_node.inputConnections.append(randomWeight)
		for hidden_node in self.hiddenLayer:
			for output_node in self.outputLayer:
				randomWeight = random.uniform(-1,1)
				#hidden_node.outputConnections.append((output_node,randomWeight))
				hidden_node.outputConnections.append(randomWeight)
				#output_node.hiddenConnections.append((hidden_node,randomWeight))
				output_node.hiddenConnections.append(randomWeight)

	def loadWeights(self):
		file_ = raw_input("Enter name of weights file: ")
		file_ = open("_4_Learn/"+file_+".data","r")
		weights = []
		for weight in file_:
			weights.append(float(weight))
		file_.close()
		for input_node in self.inputLayer:
			for hidden_node in self.hiddenLayer:
				#input_node.hiddenConnections.append((hidden_node,weights[0]))
				input_node.hiddenConnections.append(weights[0])
				#hidden_node.inputConnections.append((input_node,weights[0]))
				hidden_node.inputConnections.append(weights[0])
				weights.pop(0)
		for hidden_node in self.hiddenLayer:
			for output_node in self.outputLayer:
				#hidden_node.outputConnections.append((output_node,weights[0]))
				hidden_node.outputConnections.append(weights[0])
				#output_node.hiddenConnections.append((hidden_node,weights[0]))
				output_node.hiddenConnections.append(weights[0])
				weights.pop(0)

	def train(self):
                self.epochError = 0
                self.trainingEpoch()
                self.epochs += 1
                error = float(self.epochError) / float(len(self.inputActivations))
                print "Epoch:", self.epochs, "Count Error:", self.epochError, "Percentage Error:", error

        def test(self):
            labels = []
            step = 0
            testerr = 0
            for timeStep in self.inputActivations:
                if step % 10000 == 0:
                    print "Timestep:", step
                output = self.minusPhase(timeStep)
                if self.plusPhase(timeStep,output) == False:
                    testerr += 1
                labels.append(self.getLabel(output[0]))
                step += 1
            print "Test Count Error:", testerr
            return labels

	def saveWeights(self):
                weights = open("_4_Learn/"+raw_input("Enter name for weights: ")+".data","w")
		for node in self.inputLayer:
			for connection in node.hiddenConnections:
				weights.write(str(connection))
				weights.write("\n")
		for node in self.hiddenLayer:
			for connection in node.outputConnections:
				weights.write(str(connection))
				weights.write("\n")
		weights.close()


