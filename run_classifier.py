__author__ = 'omrim'

from util import LoadData
import sklearn.linear_model
from sklearn.neighbors import KNeighborsClassifier
from sklearn import cross_validation
from sklearn.naive_bayes import MultinomialNB
from sklearn.mixture import GMM
from sklearn.ensemble import AdaBoostClassifier
import numpy as np
from sklearn import svm
import cPickle as pickle
from util import standard_data, fix_pixels


def contrast_improve(inputs, contrast):
    new_data = [((d - 0.5) * (np.tan((contrast + 1) * np.pi/4)) + 0.5) for d in inputs]
    return new_data

def knn(training_inputs, training_labels, valid_inputs, valid_label):
    knn_class = KNeighborsClassifier(weights='distance', n_neighbors=5)

    standard_train_inputs = standard_data(training_inputs)
    standard_valid_inputs = standard_data(valid_inputs)

    fitted_knn = knn_class.fit(standard_train_inputs, np.ravel(training_labels))
    res_f = open('trained_lr.dump', 'w')
    pickle.dump(fitted_knn,res_f )
    res_f.close()
    #score_arr = sklearn.cross_validation.cross_val_score(fitted_knn, standard_train_inputs, training_labels.ravel(), scoring=None,
    #                                         cv=cross_validation.KFold(training_labels.size, 4), n_jobs=1, verbose=0,
    #                                         fit_params=None, pre_dispatch='2*n_jobs')

    accuracy = knn_class.score(standard_valid_inputs, np.ravel(valid_label))
    print accuracy
    #accuracy = knn_class.score(standard_valid_inputs, valid_label.ravel())
    #print "Accuracy for knn is:{}".format(score_arr)

def logistic_regression(training_inputs, training_labels, valid_inputs, valid_label):
    logistic_regression_solver = sklearn.linear_model.LogisticRegression(penalty='l2', dual=False, tol=0.001, C=1.0, fit_intercept=True,
                                                                         intercept_scaling=1, class_weight=None, random_state=None, solver='newton-cg',
                                                                         max_iter=150, multi_class='ovr', verbose=0, warm_start=False, n_jobs=2)
    standard_train_inputs = standard_data(training_inputs)
    standard_valid_inputs = standard_data(valid_inputs)
    fl = logistic_regression_solver.fit(standard_train_inputs, training_labels.ravel())
    res_f = open('trained_lr.dump', 'w')
    pickle.dump(fl,res_f )
    res_f.close()
    #score_arr = sklearn.cross_validation.cross_val_score(fl, standard_train_inputs, training_labels.ravel(), scoring=None,
    #                                         cv=cross_validation.KFold(training_labels.size, 4), n_jobs=1, verbose=0,
    #                                         fit_params=None, pre_dispatch='2*n_jobs')


    accuracy = fl.score(standard_valid_inputs, np.ravel(valid_label))
    print accuracy
    #print "Accuracy for logistic regression is:{}".format(score_arr)

def MoG(training_inputs, training_labels, valid_inputs, valid_label):
    standard_train_inputs = standard_data(training_inputs)
    standard_valid_inputs = standard_data(valid_inputs)    

    n_classes = 8

    #Try GMMs using different types of covariances.
    classifiers = dict((covar_type, GMM(n_components=n_classes,
                    covariance_type=covar_type, init_params='wc', n_init=10, n_iter=1000))
                   for covar_type in ['spherical', 'diag', 'tied', 'full'])

    n_classifiers = len(classifiers)

    for index, (name, classifier) in enumerate(classifiers.items()):
        # Since we have class labels for the training data, we can
        # initialize the GMM parameters in a supervised manner.
    
        # means = np.array([standard_train_inputs[training_labels == i].mean(axis=0)
        #                               for i in xrange(n_classes)])

        # classifier.means_ = np.reshape(np.array([means[training_labels]
        #                         for i in xrange(n_classes)]), (8, standard_train_inputs.shape[0]))
        # classifier.means_ = np.array([standard_train_inputs[training_labels == i].mean(axis=0)
        #                           for i in xrange(n_classes)])

        #print classifier.means_.shape[1]
        #print standard_train_inputs.T.shape[1]
        classifier.fit(standard_train_inputs)

        y_train_pred = classifier.predict(standard_train_inputs)
        train_accuracy = np.mean((y_train_pred.ravel() == training_labels.ravel())) * 100
        print 'for index {} the train accuracy is:{}'.format(index, train_accuracy)

        #y_test_pred = classifier.predict(valid_inputs.T)
        #test_accuracy = np.mean(y_test_pred.ravel() == valid_label.ravel()) * 100

        #print test_accuracy

def adaBoost(training_inputs, training_labels, valid_inputs, valid_label):
    standard_train_inputs = standard_data(training_inputs)
    standard_valid_inputs = standard_data(valid_inputs)    
    
    clf = AdaBoostClassifier(base_estimator=sklearn.linear_model.LogisticRegression(penalty='l2', dual=False, tol=0.01, C=1.0, fit_intercept=True,
                                                                         intercept_scaling=1, class_weight=None, random_state=None, solver='newton-cg',
                                                                         max_iter=100, multi_class='ovr', verbose=0, warm_start=False, n_jobs=2),
                            n_estimators=200)

    clf.fit(standard_train_inputs, training_labels.ravel())

    accuracy = clf.score(standard_train_inputs, training_labels.ravel())
    print accuracy

    valid_accuracy = clf.score(standard_valid_inputs, valid_label.ravel())
    print valid_accuracy

def  run_svm(all_data_in, all_data_labels, ids):
    from sklearn import decomposition

    # decPCA = decomposition.RandomizedPCA(n_components=None, copy=True, iterated_power=3, whiten=True, random_state=None)
    # standard_all_inputs = decPCA.fit_transform(all_data_in)
    # print "transformed train"
    # res_f = open('pcaIn.dump', 'w')
    # pickle.dump(standard_all_inputs,res_f )
    # res_f.close()

    # training_set, validation_set, train_set_labels, validation_set_labels = cross_validation.train_test_split(
    #                 standard_all_inputs, all_data_labels, test_size = 0.3, random_state=1, stratify=ids)

    training_set, validation_set, train_set_labels, validation_set_labels = cross_validation.train_test_split(
                    all_data_in, all_data_labels, test_size = 0.3, random_state=1, stratify=ids)

    # print "transformed valid"
    standard_train_inputs = fix_pixels(training_set)
    standard_valid_inputs = fix_pixels(validation_set)

    # standard_train_inputs = contrast_improve(std_train,0.5)
    # standard_valid_inputs = contrast_improve(std_valid,0.5)

    max_acc = 0

    for c in [50]:

        clf = svm.SVC(kernel='rbf', C=c, shrinking = False,decision_function_shape='ovr', tol=0.001, max_iter=-1)
        # res_f = open('traindSVM.dump', 'w')
        # pickle.dump(standard_all_inputs,res_f )
        # res_f.close()
        clf.fit(standard_train_inputs, train_set_labels.ravel())

        accuracy = clf.score(standard_valid_inputs, validation_set_labels.ravel())
        if max_acc < accuracy:
            max_acc = accuracy
            res_f = open('trained_svm.dump', 'w')
            pickle.dump(clf,res_f )
            res_f.close()
            print "the new best acc is:" , accuracy, 'the prams are g={}, c={}'.format(0,c)



def get_prior_dist(training_labels):
    stats = [0,0,0,0,0,0,0]
    for i,l in enumerate(training_labels):
        stats[l-1] += 1
    llen = len(training_labels)
    stts = [float(s) / llen for s in stats]
    print(stts)

def run_voting(training_set, train_set_labels, validation_set, validation_set_labels):
    from sklearn.ensemble import VotingClassifier
    standard_train_inputs = standard_data(training_set)
    standard_valid_inputs = standard_data(validation_set)
    kknn_class = KNeighborsClassifier(weights='uniform', n_neighbors=5)

    logistic_regression_solver = sklearn.linear_model.LogisticRegression(penalty='l2', dual=False, tol=0.01, C=1.0, fit_intercept=True,
                                                                         intercept_scaling=1, class_weight=None, random_state=None, solver='newton-cg',
                                                                         max_iter=100, multi_class='ovr', verbose=0, warm_start=False, n_jobs=2)
    svm_class = svm.SVC(decision_function_shape='ovo', tol=0.001)
    eclf1 = VotingClassifier(estimators=[('knn', kknn_class), ('lr', logistic_regression_solver), ('svm', svm_class)], voting='hard')
    eclf1.fit(standard_train_inputs,train_set_labels.ravel())

    accuracy = eclf1.score(standard_valid_inputs,validation_set_labels.ravel())
    print accuracy

def run_bagging(training_set, train_set_labels,  clsf,validation_set=None, validation_set_labels=None):
    from sklearn.ensemble import BaggingClassifier

    bgc = BaggingClassifier(base_estimator=clsf, n_estimators=11, max_samples=1.0, max_features=1.0, bootstrap=True,
                            bootstrap_features=False, oob_score=False, warm_start=False, n_jobs=1, random_state=None,
                            verbose=0)
    # standard_train_inputs = standard_data(training_set)
    # standard_valid_inputs = standard_data(validation_set)
    fbgc = bgc.fit(training_set,train_set_labels.ravel())
    if not validation_set_labels == None:
        acc = fbgc.score(validation_set,validation_set_labels.ravel())
        print(acc)
    return fbgc

def get_acc(pred, labels):
    corrects = 0
    errs = []
    for p,l in zip(pred,labels):
        corrects += int(p==l[0])
        errs.append((p,l[0]))
    return (float(corrects) / len(labels)) , errs

def create_csv(labels,fname):
    import csv

    myfile = open(fname, 'wb')
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(['Id', 'Prediction'])
    for i, l in enumerate(labels):
        wr.writerow([i+1, l])
    while i<1253:
        wr.writerow([i+1, 0])
    myfile.close()



def run_my_votin(training_set, train_set_labels, validation_set=None, validation_set_labels=None, train=True):
    from sklearn.ensemble import VotingClassifier
    from pybrain.datasets import ClassificationDataSet
    from neural_nets import load_net_and_check_errorate, net_class

    standard_valid_inputs = standard_data(validation_set)

    fixed_valid = fix_pixels(validation_set)
    if train:
        standard_train_inputs = standard_data(training_set)
        fixed_train_set = fix_pixels(training_set)
        kknn_class = KNeighborsClassifier(weights='distance', n_neighbors=5)
        kknn_class.fit(standard_train_inputs, train_set_labels.ravel())
        logistic_regression_solver = sklearn.linear_model.LogisticRegression(penalty='l2', dual=False, tol=0.001, C=1.2, fit_intercept=True,
                                                                             intercept_scaling=1, class_weight=None, random_state=None, solver='newton-cg',
                                                                             max_iter=200, multi_class='ovr', verbose=0, warm_start=False, n_jobs=2)
        svm_class = svm.SVC(kernel='rbf', C=50, shrinking = False,decision_function_shape='ovr', tol=0.001, max_iter=-1)


        # bg1 = run_bagging(standard_train_inputs, train_set_labels, kknn_class, standard_valid_inputs, validation_set_labels)
        res_f = open('bg1knn.dump', 'w')
        pickle.dump(kknn_class,res_f )
        res_f.close()
        print "Knn done"
        bg2 = run_bagging(standard_train_inputs, train_set_labels, logistic_regression_solver, standard_valid_inputs, validation_set_labels)
        res_f = open('bg2lr.dump', 'w')
        pickle.dump(bg2,res_f )
        res_f.close()
        print "done bg LR"
        bg3 = run_bagging(fixed_train_set, train_set_labels ,svm_class, fixed_valid, validation_set_labels)
        res_f = open('bg3svm.dump', 'w')
        pickle.dump(bg3,res_f )
        res_f.close()
        print "done bg svm"
        net_clf = net_class(training_set,train_set_labels)
        print "nets done"
    else:

        res_1 = open('bg1knn.dump', 'r')
        kknn_class = pickle.load(res_1)
        res_1.close()
        print "knn done"
        res_2 = open('bg2lr.dump', 'r')
        bg2 = pickle.load(res_2)
        res_2.close()
        print "LR done"
        res_3 = open('bg3svm.dump', 'r')
        bg3 = pickle.load(res_3)
        res_3.close()
        print "svm done"

        res_4 = open('bestNet.dump', 'r')
        net_clf = pickle.load(res_4)
        res_4.close()
        print "net done"

    # vds = ClassificationDataSet(1024, 8, nb_classes=8)
    # lX = standard_data(standard_valid_inputs)
    # for vd, vt in zip(lX, Y):
    #     vtarr = [int(i==vt) for i in range(0,8)]
    #     vds.addSample(vd, vtarr)
    # net_predictions = net_clf.testOnClassData(dataset=vds)

    # eclf1 = VotingClassifier(estimators=[('knn', kknn_class), ('lr', bg2), ('svm', bg3)], voting='soft')
    # eclf1.fit(standard_train_inputs,train_set_labels.ravel())
    # print "done fit votings"
    # voting_probs = eclf1.predict_proba(standard_valid_inputs)

    preds_arr = []
    pred_weights = [0.05, 0.4,0.45]
    net_weight = 0.1


    for clf in [kknn_class, bg2]:
        preds_arr.append(clf.predict_proba(standard_valid_inputs))
    preds_arr.append(bg3.predict_proba(fixed_valid))

    net_preds =[]
    for in_data in standard_valid_inputs:
        net_preds.append(net_clf.activate(in_data))

    # preds_arr.append(net_preds)
    fin_pred = []
    for i in range(len(standard_valid_inputs)):
        tmp_np = np.zeros(7)
        for w ,pp in zip(pred_weights, preds_arr):
            tmp_np += pp[i] * w
        tmp_np += net_preds[i][1:] * net_weight

        fin_pred.append(tmp_np)




    # for i,pr in enumerate(fin_pred):
    #     pr += voting_probs[i]*0.75

    fin_labels = [(np.argmax(ar, axis=0)+1) for ar in fin_pred]
    create_csv(fin_labels,'res_csv.csv')
    # print(fin_labels)
    if not validation_set_labels == None:
        fin_acc, err = get_acc(fin_labels, validation_set_labels)
        print 'The final accuracy after bagging and votig is :', fin_acc
    # print "and thats all the errors"
    # print [(x,y) for x,y in err if x==7]

    # prob_predictions = []
    # for bgc in [bg1, bg2, bg3]:
    #     prob_predictions.append(bgc.predict_proba(validation_set.ravel()))
    # prob_predictions.append(bg4.activateOnDataset(validation_set.ravel()))

    # final_pred = []
    # for ip, p in enumerate(train_set_labels):
    #     for i,v in enumerate(prob_predictions):
    #         final_pred

def run_public_test_on(class_name):

    if class_name == 'knn':
        res_1 = open('bg1knn.dump', 'r')
        clf = pickle.load(res_1)
        res_1.close()
        print "knn done"
    elif class_name == 'lr':
        res_2 = open('bg2lr.dump', 'r')
        clf = pickle.load(res_2)
        res_2.close()
        print "LR done"
    elif class_name == 'svm':
        res_3 = open('bg3svm.dump', 'r')
        clf = pickle.load(res_3)
        res_3.close()
        print "svm done"
    elif class_name == 'nn':
        res_4 = open('bestNet.dump', 'r')
        clf = pickle.load(res_4)
        res_4.close()
        print "net done"
    validation_set= LoadData('public_test_images.mat', False, False)
    fixed_valid = fix_pixels(validation_set)
    fin_pred = clf.predict_proba(fixed_valid)
    fin_labels = [(np.argmax(ar, axis=0)+1) for ar in fin_pred]
    create_csv(fin_labels,'res_csv.csv')


if __name__ == '__main__':
    # training_sett, train_set_labelts, validation_set, validation_set_labels = LoadData('labeled_images.mat', True, True)
    #training_inputs, valid_inputs, training_labels, valid_label = cross_validation.train_test_split(train_inputs, train_targets, test_size=0.3, rlogistic_regression(training_set, train_set_labels, validation_set, validation_set_labels)
    # knn(training_set, train_set_labels, validation_set, validation_set_labels)
    #logistic_regression(training_set, train_set_labels, validation_set, validation_set_labels)
    # MoG(training_set, train_set_labels, validation_set, validation_set_labels)
    #adaBoost(training_set, train_set_labels, validation_set, validation_set_labels)
    # inp, labels, ids = LoadData('labeled_images.mat', True, False)
    # run_svm(inp, labels, ids)
    #run_bagging(training_set, train_set_labels, validation_set, validation_set_labels, clsf)
    #run_voting(training_set, train_set_labels, validation_set, validation_set_labels)

    # create_csv(range(11,21))

    # training_set, train_set_labels, idst = LoadData('labeled_images.mat', True, False)
    # validation_set= LoadData('public_test_images.mat', False, False)
    # run_my_votin(training_set, train_set_labels,validation_set, None, False)
    run_public_test_on('svm')
