def metrics_threshold(steps, threshold, step_len):
    """
    Calculates the metrics necessary for the threshold given.
    :param steps: the threshold steps
    :param threshold: the target threshold
    :param step_len: the length of the score step
    :return: the metrics calculated for the given threshold
    """
    steps_below = filter(lambda step: step.step < threshold / step_len, steps)
    steps_above = filter(lambda step: step.step >= threshold / step_len, steps)

    if not steps_below:
        metrics_below = [0, 0.0, 0, 0.0]
    else:
        metrics_below = map(sum, zip(*(map(lambda s: s.tuple(), steps_below))))

    if not steps_above:
        metrics_above = [0, 0.0, 0, 0.0]
    else:
        metrics_above = map(sum, zip(*(map(lambda s: s.tuple(), steps_above))))

    tp_count = metrics_above[2]

    tp_money = metrics_above[3]

    fp_count = metrics_above[0]

    fp_money= metrics_above[1]

    tn_count = metrics_below[0]

    fn_count = metrics_below[2]

    fn_money = metrics_below[3]

    if tp_count + fn_count == 0:
        trx_recall = 0.0
    else:
        trx_recall = 100.0 * tp_count / (tp_count + fn_count)

    if tp_money + fn_money == 0.0:
        money_recall = 0.0
    else:
        money_recall = 100.0 * tp_money / (tp_money + fn_money)

    if tp_count + fp_count == 0:
        trx_precision = 0.0
    else:
        trx_precision = 100.0 * tp_count / (tp_count + fp_count)

    if fp_count == 0 or tp_count == 0:
        trx_precision_1n = 100000000.0
    else:
        trx_precision_1n = 1.0 * fp_count / tp_count

    if tn_count + fp_count == 0:
        fpr = 100.0
    else:
        fpr = 100.0 * fp_count / (tn_count + fp_count)


    # booking specific metrics
    if trx_recall == 0 or trx_precision == 0:
        f1_score = 0.0
    else:
        f1_score = 2.0 * (trx_recall * trx_precision) / (trx_recall + trx_precision)

    fn_cost = 1.1  * fn_money + 61.55 * fn_count
    fp_cost = 0.15 * fp_money



    return threshold, trx_recall, money_recall, trx_precision, trx_precision_1n, fpr, f1_score, fn_cost, fp_cost


def write_summary(metrics, summary_file):
    """
    Writes the metrics calculated to the file given
    :param metrics: the metrics to write in the file
    :param summary_file: the summary file
    """
    summary_file.write('   {0}   |'.format('{0}'.format(metrics[0]).rjust(4)))
    summary_file.write('    {0}   |'.format('{0:.2f}'.format(metrics[1]).rjust(5)))
    summary_file.write('     {0}    |'.format('{0:.2f}'.format(metrics[2]).rjust(5)))
    summary_file.write('    {0}    |'.format('{0:.2f}'.format(metrics[3]).rjust(5)))
    summary_file.write('      {0}     |'.format('{0:.2f}'.format(metrics[4]).rjust(6)))
    summary_file.write('    {0}    |'.format('{0:.2f}'.format(metrics[5]).rjust(5)))
    summary_file.write('     {0}     |'.format('{0:.2f}'.format(metrics[6]).rjust(5)))
    summary_file.write('     {0}     |'.format('{0:.2f}'.format(metrics[7]).rjust(9)))
    summary_file.write('      {0}      |'.format('{0:.2f}'.format(metrics[8]).rjust(9)))
    summary_file.write(' {0} \n'.format('{0:.2f}'.format(metrics[7] + metrics[8]).rjust(9)))



def print_header(summary_file):
    """
    Prints the header for a table of metrics in the metrics summary file
    :param summary_file: the metrics summary file
    """
    summary_file.write('===============\n')
    summary_file.write('Threshold | Trx Recall | Money Recall | Precision % |  Precision 1:n  |     FPR     |    F1 Score   |     FN cost       |       FP cost       | Total Cost\n')


def fixed_metrics(steps, summary_file, step_len):
    """
    Searches for the thresholds that are closer to a 1% FPR and 1:2 Precision and 73% money recall and prints their metrics in the summary file
    :param steps: the threshold steps and their metrics
    :param summary_file: the metrics summary file
    :param step_len: the length of the score step
    """
    target_fpr = 1.0
    # target_precision1n = 2.0
    # target_money_recall = 73

    max_f1_score = 0
    min_total_cost = float("inf")

    closest_fpr = metrics_threshold(steps, 0, step_len)
    # closest_precision1n = closest_fpr
    # closest_money_recall = closest_fpr
    closest_f1_score = closest_fpr
    closest_cost = closest_fpr

    for step in steps:
        step_metrics = metrics_threshold(steps, step.step * step_len, step_len)

        if abs(step_metrics[5] - target_fpr) < abs(closest_fpr[5] - target_fpr):
            closest_fpr = step_metrics

        # if abs(step_metrics[4] - target_precision1n) < abs(closest_precision1n[4] - target_precision1n):
        #     closest_precision1n = step_metrics

        # if abs(step_metrics[2] - target_money_recall) < abs(closest_money_recall[2] - target_money_recall):
        #     closest_money_recall = step_metrics
        
        if step_metrics[6] > max_f1_score:
            max_f1_score = step_metrics[6]
            closest_f1_score = step_metrics

        if step_metrics[7] + step_metrics[8] < min_total_cost:
            min_total_cost = step_metrics[7] + step_metrics[8]
            closest_cost = step_metrics

    print_header(summary_file)
    write_summary(closest_fpr, summary_file)
    # write_summary(closest_precision1n, summary_file)
    # write_summary(closest_money_recall, summary_file)
    write_summary(closest_f1_score, summary_file)
    write_summary(closest_cost, summary_file)


def metrics_summary(steps, filename, step_len):
    """
    Creates a metrics summary file with the relevant metrics for thresholds 500, 700 and 900
    :param steps: the threshold steps and their metrics
    :param step_len: the length of the score step
    """
    summary_file = open(filename, 'w')
    summary_file.write('Metrics Summary\n')

    print_header(summary_file)
    #    for threshold in xrange(100, 910, 100):
    #        write_summary(metrics_threshold(steps, threshold), summary_file)
    write_summary(metrics_threshold(steps, 500, step_len), summary_file)
    write_summary(metrics_threshold(steps, 750, step_len), summary_file)
    write_summary(metrics_threshold(steps, 875, step_len), summary_file)
    write_summary(metrics_threshold(steps, 950, step_len), summary_file)
    write_summary(metrics_threshold(steps, 980, step_len), summary_file)

    fixed_metrics(steps, summary_file, step_len)
    summary_file.close()
