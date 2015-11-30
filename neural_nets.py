__author__ = 'omrim'

from util import LoadData
import sklearn.linear_model
from sklearn.neighbors import KNeighborsClassifier
from sklearn import cross_validation
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from run_classifier import standard_data
import cPickle as pickle
####################NN imports#############
from pybrain.tools.shortcuts import buildNetwork
from pybrain.tools.neuralnets import NNclassifier

from pybrain.structure import TanhLayer
from pybrain.structure import SoftmaxLayer
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import ClassificationDataSet
from pybrain.utilities import percentError

def net_class(ustraining_set, train_set_labels, usvalidation_set, validation_set_labels):

    ltraining_set = standard_data(ustraining_set)
    lvalidation_set = standard_data(usvalidation_set)
    net = buildNetwork(1024, 100, 8,outclass=SoftmaxLayer)

    ds = ClassificationDataSet(1024, 8, nb_classes=8)
    for d,t in zip(ltraining_set, train_set_labels):
        tarr = [int(i==t) for i in range(0,8)]
        ds.addSample(d, tarr)

    vds = ClassificationDataSet(1024, 8, nb_classes=8)
    for vd, vt in zip(lvalidation_set, validation_set_labels):
        vtarr = [int(i==vt) for i in range(0,8)]
        vds.addSample(vd, vtarr)
    tot_min_err = 100.0
    best_l = 0.0
    best_w = 0.0
    obest_e = 0
    for l in [0.001, 0.002, 0.004, 0.005 ]:
        for w in [0.05, 0.06, 0.7, 0.8, 0.9]:
            net = buildNetwork(1024, 100, 8,outclass=SoftmaxLayer)
            trainer = BackpropTrainer(net, ds, learningrate=l, momentum=0, weightdecay=w, batchlearning=False,verbose=True)
            cmin_err = 100.0
            flag = True
            best_e = 0
            e = 0
            while flag:
                flag = False
                trnresult = 100.0
                tstresult = 100.0
                for i in range(20):
                    e += 1
                    trainer.trainEpochs(1)

                    trnresult = percentError( trainer.testOnClassData(),
                                              train_set_labels )



                    tstresult = percentError( trainer.testOnClassData(dataset=vds ), validation_set_labels )
                    if cmin_err >= tstresult:
                        cmin_err = tstresult
                        print "copt err ", tstresult
                        best_e = e
                        flag = True

                # print "epoch: %4d" % trainer.totalepochs, \
                #       "  train error: %5.2f%%" % trnresult, \
                #    "  test error: %5.2f%%" % cmin_err

            if tot_min_err > cmin_err:

                tot_min_err = cmin_err

                best_l = l
                best_w = w
                obest_e = best_e
                print "new opt err:{}, for LR: {}, WD:{}, NE:{} ".format(tot_min_err, best_l, best_w, obest_e)
                net.sorted = False
                net.sortModules()
                res_f = open('bestNet.dump', 'w')
                pickle.dump(net,res_f )
                res_f.close()


def load_net_and_check_errorate(X,Y):

    res_f = open('testNetwork.dump', 'r')
    nnet = pickle.load(res_f)
    nnet.sorted = False
    nnet.sortModules()
    vds = ClassificationDataSet(1024, 8, nb_classes=8)
    lX = standard_data(X)
    for vd, vt in zip(lX, Y):
        vtarr = [int(i==vt) for i in range(0,8)]
        vds.addSample(vd, vtarr)
    ttrainer = BackpropTrainer(nnet, vds, learningrate=0.005, momentum=0, weightdecay=0.05, batchlearning=False,verbose=True)
    ttstresult = percentError( ttrainer.testOnClassData(), Y )



    print " Classification rate for the trained Neural net is: %5.2f%%" % (100 - ttstresult)
    res_f.close()

if __name__ == '__main__':

    training_set, train_set_labels, validation_set, validation_set_labels = LoadData('labeled_images.mat', True, False)

    net_class(training_set, train_set_labels, validation_set, validation_set_labels)

    #load_net_and_check_errorate(validation_set, validation_set_labels)