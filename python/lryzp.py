#!/usr/bin/python
import sys
import random
import math
import operator
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error


bufferCaseNum = 1000000
#bufferCaseNum = 10
eta = 0.01
lamb = 1E-6
featWeight = {}
trainRounds = 10
random.seed(10)
initWeight = 0.05

def nextInitWeight():
    return (random.random() - 0.5) * initWeight

def ints(s):
    res = []
    for ss in s:
        res.append(int(ss))
    return res

def sigmoid(p):
    return 1.0 / (1.0 + math.exp(-p))


if len(sys.argv) < 3:
    print 'Usage: train.yzx.txt train.yzp.txt test.yzx.txt test.yzp.txt'
    exit(-1)


for round in range(0, trainRounds):
    # train for this round
    fi = open(sys.argv[1], 'r')
    lineNum = 0
    trainData = []
    for line in fi:
        lineNum = (lineNum + 1) % bufferCaseNum
        trainData.append(ints(line.replace(":1", "").split()))
        if lineNum == 0:
            for data in trainData:
                clk = data[0]
                mp = data[1]
                fsid = 2 # feature start id
                # predict
                pred = 0.0
                for i in range(fsid, len(data)):
                    feat = data[i]
                    if feat not in featWeight:
                        featWeight[feat] = nextInitWeight()
                    pred += featWeight[feat]
                pred = sigmoid(pred)
                # start to update weight
                # w_i = w_i + learning_rate * [ (y - p) * x_i - lamb * w_i ] 
                for i in range(fsid, len(data)):
                    feat = data[i]
                    featWeight[feat] = featWeight[feat] * (1 - lamb) + eta * (clk - pred)
            trainData = []

    if len(trainData) > 0:
        for data in trainData:
            clk = data[0]
            mp = data[1]
            fsid = 2 # feature start id
            # predict
            pred = 0.0
            for i in range(fsid, len(data)):
                feat = data[i]
                if feat not in featWeight:
                    featWeight[feat] = nextInitWeight()
                pred += featWeight[feat]
            pred = sigmoid(pred)
            # start to update weight
            # w_i = w_i + learning_rate * [ (y - p) * x_i - lamb * w_i ]
            for i in range(fsid, len(data)):
                feat = data[i]
                featWeight[feat] = featWeight[feat] * (1 - lamb) + eta * (clk - pred)
    fi.close()

    '''
    # test for this round
    y = []
    yp = []
    fi = open(sys.argv[3], 'r')
    for line in fi:
        data = ints(line.replace(":1", "").split())
        clk = data[0]
        mp = data[1]
        fsid = 2 # feature start id
        pred = 0.0
        for i in range(fsid, len(data)):
            feat = data[i]
            if feat in featWeight:
                pred += featWeight[feat]
        pred = sigmoid(pred)
        y.append(clk)
        yp.append(pred)
    fi.close()
    auc = roc_auc_score(y, yp)
    rmse = math.sqrt(mean_squared_error(y, yp))
    print str(round) + '\t' + str(auc) + '\t' + str(rmse)
    '''

# output the prediction of train.yzx.base
fi = open(sys.argv[1], 'r')
fo = open(sys.argv[2], 'w')

for line in fi:
    data = ints(line.replace(":1", "").split())
    pred = 0.0
    for i in range(1, len(data)):
        feat = data[i]
        if feat in featWeight:
            pred += featWeight[feat]
    pred = sigmoid(pred)
    fo.write('%d\t%d\t%.6f\n' % (data[0], data[1], pred))
print 'pctr train finished'
fo.close()
fi.close()


# output the prediction of train.yzx.bid.txt
fi = open(sys.argv[3], 'r')  # train.yzx.bid.txt
fo = open(sys.argv[4], 'w')  # train.yz

for line in fi:
    data = ints(line.replace(":1", "").split())
    pred = 0.0
    for i in range(1, len(data)):
        feat = data[i]
        if feat in featWeight:
            pred += featWeight[feat]
    pred = sigmoid(pred)
    fo.write('%.6f\n' % pred)
fo.close()
fi.close()



