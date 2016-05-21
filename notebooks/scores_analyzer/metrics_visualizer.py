import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import metrics_analyzer

def init_figure():
    """
    Initialize the figure with the configuration of text and format
    """
    plt.xlabel('Score threshold')
    plt.title('Metrics v.s threshold')

    fmt = '%.0f%%' # Format the percentage ticks, e.g. '40%'
    yticks = mtick.FormatStrFormatter(fmt)
    ax = plt.gca()
    ax.yaxis.set_major_formatter(yticks)
    plt.yticks(np.arange(0, 101, 5))
    plt.xticks(np.arange(0, 1001, 50))
    plt.grid()


def plot_metrics(steps, threshold):
    """
    Plot the figure (Money Recall, FPR, Precision) v.s Score Threshold
    :param steps: the threshold steps and their metrics
    :param threshold: the threshold according to the FPR from scores_analyzer 
    """
    plt.axis([threshold, 1000, 0 , 100])

    x_score = []
    y_money_recall = []
    y_fpr = []
    y_precision = []
    for step in steps:
        if step.step * 10 >= threshold:
            step_metrics = metrics_analyzer.metrics_threshold(steps, step.step * 10)
            x_score.append(step_metrics[0])
            y_money_recall.append(step_metrics[2])
            y_fpr.append(step_metrics[5])
            y_precision.append(step_metrics[3])

    line1, = plt.plot(x_score, y_money_recall, marker='.', label='Money Recall')
    line2, = plt.plot(x_score, y_fpr, marker='.', label='FPR')
    line3, = plt.plot(x_score, y_precision, marker='.', label='Precision')
    
    ax = plt.gca()
    ax.legend((line1, line2, line3), ('Money Recall','FPR','Precision'), loc='upper left')



def find_start_threshold(steps, target_fpr):
    """
    :param steps: the threshold steps and their metrics
    :param target_fpr: the FPR from scores_analyzer
    """
    closest_fpr = metrics_analyzer.metrics_threshold(steps, 0)

    for step in steps:
        step_metrics = metrics_analyzer.metrics_threshold(steps, step.step * 10)

        if abs(step_metrics[5] - target_fpr) < abs(closest_fpr[5] - target_fpr):
            closest_fpr = step_metrics

    return closest_fpr[0]

def metrics_visualize(steps, start_fpr, fig_filename):
    """
    Creates a metrics figure with the relevant metrics start from the FPR from scores_analyzer
    :param steps: the threshold steps and their metrics
    :param target_fpr: the FPR pass in from scores_analyzer 
    :param fig_filename: the path to save the figure
    """
    init_figure()
    threshold = find_start_threshold(steps, start_fpr)
    plot_metrics(steps, threshold)
    plt.savefig(fig_filename)
    plt.close()
