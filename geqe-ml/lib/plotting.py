import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def updateMonitorPlot(mPX, mPY, mSL, jobNm):
    plt.xlabel("Application Step")
    plt.ylabel("Time to complete")
    plt.suptitle(jobNm+" Progress")
    plt.subplots_adjust(bottom=0.45)
    ax = plt.subplot()
    ax.bar(mPX, mPY, width=1.0)
    ax.set_xticks(map(lambda x: x-0.5, range(1,len(mPX)+1)))
    ax.set_xticklabels(mSL,rotation=45)
    ax.set_yscale('log')
    plt.savefig("monitorFiles/"+jobNm+".png")

def generateROCCurve(tAndP, nPos, nNeg, jobNm):
    print "Positive Points:", nPos, "\tNegative Points:", nNeg
    tpr = []
    fpr = []
    for thresh in map(lambda x: (10.-1.*x)/10.,range(21)):
        # tp -> condition positive, predicted positive
        # fp -> condition negative, predicted positive
        # tn -> condition negative, predicted negative
        # fn -> condition positive, predicted negative
        true_positive  = 0
        false_positive = 0
        true_negative  = 0
        false_negative = 0
        for point in tAndP:
            if point[0] == 1. and point[1] >= thresh:
                true_positive = true_positive + 1
            elif point[0] == 1. and point[1] < thresh:
                false_negative = false_negative + 1
            elif point[0] == -1. and point[1] >= thresh:
                false_positive = false_positive + 1
            elif point[0] == -1. and point[1] < thresh:
                true_negative = true_negative + 1
        print "\tThreshold: ",thresh
        print "\t\tTP:", true_positive, "FP", false_positive, "FN", false_negative, "TN", true_negative
        tpr.append((1.*true_positive)/(1.*nPos))
        fpr.append((1.*false_positive)/(1.*nNeg))

    plt.xlabel("False Positive Rate (1-Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity)")
    plt.plot(fpr, tpr, label="ROC for job:"+jobNm)
    plt.savefig("monitorFiles/"+jobNm+".png")