from .FeatureGenerator import *
from .TfidfFeatureGenerator import *
import pandas as pd
import numpy as np
from scipy.sparse import vstack
import pickle
from sklearn.decomposition import TruncatedSVD
from .helpers import *

class SvdFeatureGenerator(FeatureGenerator):
    """
    This module takes the TF-IDF features and applies 
    Singular-Value Decomposition to them to obtain a 
    compact, dense vector representation of the headline 
    and body respectively. This procedure is well known 
    and corresponds to finding the latent topics involved 
    in the corpus and represent each headline/body text as 
    a mixture of these topics. The cosine similarities between 
    the SVD features of headline and body text are also computed. 
    This similarity metric is very indicative of whether the 
    body is related to the headline or not.
    """

    def __init__(self, name='svdFeatureGenerator'):
        super(SvdFeatureGenerator, self).__init__(name)


    def process(self, df):
        
        n_train = df[~df['target'].isnull()].shape[0]
        print ('SvdFeatureGenerator, n_train:',n_train)
        n_test  = df[df['target'].isnull()].shape[0]
        print ('SvdFeatureGenerator, n_test:',n_test)

        tfidfGenerator = TfidfFeatureGenerator('tfidf')
        featuresTrain = tfidfGenerator.read('train')
        xHeadlineTfidfTrain, xBodyTfidfTrain = featuresTrain[0], featuresTrain[1]
        
        xHeadlineTfidf = xHeadlineTfidfTrain
        xBodyTfidf = xBodyTfidfTrain
        if n_test > 0:
            # test set is available
            featuresTest  = tfidfGenerator.read('test')
            xHeadlineTfidfTest,  xBodyTfidfTest  = featuresTest[0],  featuresTest[1]
            xHeadlineTfidf = vstack([xHeadlineTfidfTrain, xHeadlineTfidfTest])
            xBodyTfidf = vstack([xBodyTfidfTrain, xBodyTfidfTest])
	    
        # compute the cosine similarity between truncated-svd features
        svd = TruncatedSVD(n_components=50, n_iter=15)
        xHBTfidf = vstack([xHeadlineTfidf, xBodyTfidf])
        svd.fit(xHBTfidf) # fit to the combined train-test set (or the full training set for cv process)
        print ('xHeadlineTfidf.shape:')
        print (xHeadlineTfidf.shape)
        xHeadlineSvd = svd.transform(xHeadlineTfidf)
        print ('xHeadlineSvd.shape:')
        print (xHeadlineSvd.shape)
        
        xHeadlineSvdTrain = xHeadlineSvd[:n_train, :]
        outfilename_hsvd_train = "train.headline.svd.pkl"
        with open("../saved_data/" + outfilename_hsvd_train, "wb") as outfile:
            pickle.dump(xHeadlineSvdTrain, outfile, -1)
        print ('headline svd features of training set saved in %s' % outfilename_hsvd_train)
        
        if n_test > 0:
            # test set is available
            xHeadlineSvdTest = xHeadlineSvd[n_train:, :]
            outfilename_hsvd_test = "test.headline.svd.pkl"
            with open("../saved_data/" + outfilename_hsvd_test, "wb") as outfile:
                pickle.dump(xHeadlineSvdTest, outfile, -1)
            print ('headline svd features of test set saved in %s' % outfilename_hsvd_test)

        xBodySvd = svd.transform(xBodyTfidf)
        print ('xBodySvd.shape:')
        print (xBodySvd.shape)
        
        xBodySvdTrain = xBodySvd[:n_train, :]
        outfilename_bsvd_train = "train.body.svd.pkl"
        with open("../saved_data/" + outfilename_bsvd_train, "wb") as outfile:
            pickle.dump(xBodySvdTrain, outfile, -1)
        print ('body svd features of training set saved in %s' % outfilename_bsvd_train)
        
        if n_test > 0:
            # test set is available
            xBodySvdTest = xBodySvd[n_train:, :]
            outfilename_bsvd_test = "test.body.svd.pkl"
            with open("../saved_data/" + outfilename_bsvd_test, "wb") as outfile:
                pickle.dump(xBodySvdTest, outfile, -1)
            print ('body svd features of test set saved in %s' % outfilename_bsvd_test)

        simSvd = np.asarray(list(map(cosine_sim, xHeadlineSvd, xBodySvd)))[:, np.newaxis]
        print ('simSvd.shape:')
        print (simSvd.shape)

        simSvdTrain = simSvd[:n_train]
        outfilename_simsvd_train = "train.sim.svd.pkl"
        with open("../saved_data/" + outfilename_simsvd_train, "wb") as outfile:
            pickle.dump(simSvdTrain, outfile, -1)
        print ('svd sim. features of training set saved in %s' % outfilename_simsvd_train)
        
        if n_test > 0:
            # test set is available
            simSvdTest = simSvd[n_train:]
            outfilename_simsvd_test = "test.sim.svd.pkl"
            with open("../saved_data/" + outfilename_simsvd_test, "wb") as outfile:
                pickle.dump(simSvdTest, outfile, -1)
            print ('svd sim. features of test set saved in %s' % outfilename_simsvd_test)

        return 1


    def read(self, header='train'):

        filename_hsvd = "%s.headline.svd.pkl" % header
        with open("../saved_data/" + filename_hsvd, "rb") as infile:
            xHeadlineSvd = pickle.load(infile)

        filename_bsvd = "%s.body.svd.pkl" % header
        with open("../saved_data/" + filename_bsvd, "rb") as infile:
            xBodySvd = pickle.load(infile)

        filename_simsvd = "%s.sim.svd.pkl" % header
        with open("../saved_data/" + filename_simsvd, "rb") as infile:
            simSvd = pickle.load(infile)

        print ('xHeadlineSvd.shape:')
        print (xHeadlineSvd.shape)
        #print (type(xHeadlineSvd))
        print ('xBodySvd.shape:')
        print (xBodySvd.shape)
        #print (type(xBodySvd))
        print ('simSvd.shape:')
        print (simSvd.shape)
        #print (type(simSvd))

        return [xHeadlineSvd, xBodySvd, simSvd.reshape(-1, 1)]
        #return [simSvd.reshape(-1, 1)]

