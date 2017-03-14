#!/usr/bin/python
# coding:utf8

'''
Created on Nov 28, 2010
Adaboost is short for Adaptive Boosting
@author: Peter/jiangzhonglian
'''
from numpy import *


def loadSimpData():
    """ 测试数据
    Returns:
        dataArr   feature对应的数据集
        labelArr  feature对应的分类标签
    """
    dataArr = array([[1., 2.1], [2., 1.1], [1.3, 1.], [1., 1.], [2., 1.]])
    labelArr = [1.0, 1.0, -1.0, -1.0, 1.0]
    return dataArr, labelArr


def stumpClassify(dataMat, dimen, threshVal, threshIneq):
    """stumpClassify(将数据集，按照feature列的value进行 二元切分比较来赋值)

    Args:
        dataMat  Matrix数据集
        dimen 特征列
        threshVal 特征列要比较的值
    Returns:
        retArray 结果集
    """
    retArray = ones((shape(dataMat)[0], 1))
    # dataMat[:, dimen] 表示数据集中第dimen列的所有值
    # print '-----', threshIneq, dataMat[:, dimen], threshVal
    if threshIneq == 'lt':
        retArray[dataMat[:, dimen] <= threshVal] = -1.0
    else:
        retArray[dataMat[:, dimen] > threshVal] = -1.0
    return retArray


def buildStump(dataArr, labelArr, D):

    # 转换数据
    dataMat = mat(dataArr)
    labelMat = mat(labelArr).T
    # m行 n列
    m, n = shape(dataMat)

    # 初始化数据
    numSteps = 10.0
    bestStump = {}
    bestClasEst = mat(zeros((m, 1)))
    # 初始化的最小误差为无穷大
    minError = inf

    # 循环所有的feature列
    for i in range(n):
        rangeMin = dataMat[:, i].min()
        rangeMax = dataMat[:, i].max()
        # print 'rangeMin=%s, rangeMax=%s' % (rangeMin, rangeMax)
        # 计算每一份的元素个数
        stepSize = (rangeMax-rangeMin)/numSteps
        # 分成-1～numSteps= 1+numSteps份, 加本身是需要+1的
        for j in range(-1, int(numSteps)+1):
            # go over less than and greater than
            for inequal in ['lt', 'gt']:
                # 如果是-1，那么得到rangeMin-stepSize; 如果是numSteps，那么得到rangeMax
                threshVal = (rangeMin + float(j) * stepSize)
                # 对单层决策树进行简单分类
                predictedVals = stumpClassify(dataMat, i, threshVal, inequal)
                # print predictedVals
                errArr = mat(ones((m, 1)))
                # 正确为0，错误为1
                errArr[predictedVals == labelMat] = 0
                # 计算 平均每个特征的概率0.2*错误概率的总和为多少，就知道错误率多高
                # calc total error multiplied by D
                weightedError = D.T*errArr
                '''
                dim       表示 feature列
                threshVal 表示树的分界值
                inequal   表示计算树左右颠倒的错误率的情况
                weightedError 表示整体结果的错误率
                '''
                # print "split: dim %d, thresh %.2f, thresh ineqal: %s, the weighted error is %.3f" % (i, threshVal, inequal, weightedError)
                if weightedError < minError:
                    minError = weightedError
                    bestClasEst = predictedVals.copy()
                    bestStump['dim'] = i
                    bestStump['thresh'] = threshVal
                    bestStump['ineq'] = inequal
    return bestStump, minError, bestClasEst


def adaBoostTrainDS(dataArr, labelArr, numIt=40):
    weakClassArr = []
    m = shape(dataArr)[0]
    # 初始化 init D to all equal
    D = mat(ones((m, 1))/m)
    aggClassEst = mat(zeros((m, 1)))
    for i in range(numIt):
        # build Stump
        bestStump, error, classEst = buildStump(dataArr, labelArr, D)
        # print "D:", D.T
        # calc alpha, throw in max(error,eps) to account for error=0
        alpha = float(0.5*log((1.0-error)/max(error, 1e-16)))
        bestStump['alpha'] = alpha
        # store Stump Params in Array
        weakClassArr.append(bestStump)

        # print "alpha=%s, classEst=%s, bestStump=%s, error=%s " % (alpha, classEst.T, bestStump, error)
        # -1主要是下面求e的-alpha次方； 如果判断正确，乘积为1，否则为-1，这样就可以算出分类的情况了
        expon = multiply(-1*alpha*mat(labelArr).T, classEst)
        # print 'expon=', -1*alpha*mat(labelArr).T, classEst, expon
        # 计算e的expon次方，然后计算得到一个综合的概率的值
        # 结果发现： 正确的alpha的权重值变小了，错误的变大了。也就说D里面分类的权重值变了。（可以举例验证，假设：alpha=0.6，什么的）
        D = multiply(D, exp(expon))
        D = D/D.sum()
        print "D: ", D.T
        # 计算分类结果的值，在上一轮结果的基础上，进行加和操作
        # calc training error of all classifiers, if this is 0 quit for loop early (use break)
        aggClassEst += alpha*classEst
        print "aggClassEst: ", aggClassEst.T
        # sign 判断正为1， 0为0， 负为-1，通过最终加和的权重值，判断符号。
        # 结果为：错误的样本标签集合，因为是 !=,那么结果就是0 正, 1 负
        aggErrors = multiply(sign(aggClassEst) != mat(labelArr).T, ones((m, 1)))
        errorRate = aggErrors.sum()/m
        print "total error=%s " % (errorRate)
        if errorRate == 0.0:
            break
    return weakClassArr, aggClassEst


if __name__ == "__main__":
    dataArr, labelArr = loadSimpData()
    print '-----\n', dataArr, '\n', labelArr

    # D表示最初，对1进行均分为5份，平均每一个初始的概率都为0.2
    D = mat(ones((5, 1))/5)
    # print '-----', D

    # print buildStump(dataArr, labelArr, D)
    weakClassArr, aggClassEst = adaBoostTrainDS(dataArr, labelArr, 9)
    print weakClassArr




def loadDataSet(fileName):      #general function to parse tab -delimited floats
    numFeat = len(open(fileName).readline().split('\t')) #get number of fields 
    dataArr = []
    labelArr = []
    fr = open(fileName)
    for line in fr.readlines():
        lineArr = []
        curLine = line.strip().split('\t')
        for i in range(numFeat-1):
            lineArr.append(float(curLine[i]))
        dataArr.append(lineArr)
        labelArr.append(float(curLine[-1]))
    return dataArr, labelArr




def adaClassify(datToClass,classifierArr):
    dataMatrix = mat(datToClass)#do stuff similar to last aggClassEst in adaBoostTrainDS
    m = shape(dataMatrix)[0]
    aggClassEst = mat(zeros((m,1)))
    for i in range(len(classifierArr)):
        classEst = stumpClassify(dataMatrix,classifierArr[i]['dim'],\
                                 classifierArr[i]['thresh'],\
                                 classifierArr[i]['ineq'])#call stump classify
        aggClassEst += classifierArr[i]['alpha']*classEst
        print aggClassEst
    return sign(aggClassEst)

def plotROC(predStrengths, classLabels):
    import matplotlib.pyplot as plt
    cur = (1.0,1.0) #cursor
    ySum = 0.0 #variable to calculate AUC
    numPosClas = sum(array(classLabels)==1.0)
    yStep = 1/float(numPosClas); xStep = 1/float(len(classLabels)-numPosClas)
    sortedIndicies = predStrengths.argsort()#get sorted index, it's reverse
    fig = plt.figure()
    fig.clf()
    ax = plt.subplot(111)
    #loop through all the values, drawing a line segment at each point
    for index in sortedIndicies.tolist()[0]:
        if classLabels[index] == 1.0:
            delX = 0; delY = yStep;
        else:
            delX = xStep; delY = 0;
            ySum += cur[1]
        #draw line from cur to (cur[0]-delX,cur[1]-delY)
        ax.plot([cur[0],cur[0]-delX],[cur[1],cur[1]-delY], c='b')
        cur = (cur[0]-delX,cur[1]-delY)
    ax.plot([0,1],[0,1],'b--')
    plt.xlabel('False positive rate'); plt.ylabel('True positive rate')
    plt.title('ROC curve for AdaBoost horse colic detection system')
    ax.axis([0,1,0,1])
    plt.show()
    print "the Area Under the Curve is: ",ySum*xStep