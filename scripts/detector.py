import numpy as np
import pickle as pkl
from skimage.feature import hog
from sklearn.svm import LinearSVC

class FaceDetector:
	"""A linear SVM face detector."""

	def __init__(self, model=None):
		if model:
			self.clf = pkl.load(open(model, 'rb'))
		else:
			self.clf = LinearSVC(penalty='l2', loss='hinge', max_iter=5000)

	def compute_hog(self, x):
		""" Compute and return HOG features given an input x. """
		return hog(x, block_norm='L1', visualize=False, multichannel=True)

	def detect(self, x):
		# Convert input image x into np.float64 if necessary
		if x.dtype != np.float64:
			x = (x / 256).astype(np.float64)

		# Convert x into HOG features
		hog_x = self.compute_hog(x)

		# Check if x is a face
		return self.clf.predict([hog_x])