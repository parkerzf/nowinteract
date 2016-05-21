#!/usr/bin/env python

import sys
import csv
import metrics_analyzer
#import metrics_visualizer

class StepMetrics:
    """ Class that holds the metrics for a given score step """
    def __init__(self, step):
        self.step = step
        self.not_fraud_count = 0
        self.not_fraud_money = 0.0
        self.fraud_count = 0
        self.fraud_money = 0.0

    def tuple(self):
        return self.not_fraud_count, self.not_fraud_money, self.fraud_count, self.fraud_money

# maximum number of errors allowed in the analysis
max_errors = 10

def is_fraud(data):
    """
    Identifies if the transaction was fraud
    :param data: the data in the transaction
    :return: true if the transaction was fraud, false otherwise
    """
    return data[1] == 1

def is_cp(data):
    """
    Identifies if the transaction was card present
    :param data: the data in the transaction
    :return: true if the transaction was fraud, false otherwise
    """
    return data[3] == 1

def extract_data(scored_instance_val, score_idx, fraud_label_idx, amount_idx, cp_idx, err_log, line):
    """
    Extracts from the scored instance the data necessary for the score analysis:
        * Score
        * Fraud Label
        * Amount
        * CP/CNP Label

    :param scored_instance_val: the values in the scored instance
    :param score_idx: index of the score column
    :param fraud_label_idx: index of the fraud label column
    :param amount_idx: index of the amount column
    :param cp_idx: index of the cp/cnp label column
    :param err_log: the file where errors should be logged
    :param line: the line number for the current scored instance
    :return: the data extracted
    """
    try:
        # score should be a floating point value between 0.0 and 1.0
        score = float(scored_instance_val[score_idx])
        
        if score < 0.0 or score > 1.01:
            err_log.write('{}: Score \'{}\' invalid.\n'.format(line, score))
            return None
    except ValueError:
        err_log.write('{}: Score \'{}\' not a float.\n'.format(line, scored_instance_val[score_idx]))
        return None

    try:
        # fraud label should be either 0 or 1
        fraud_label = int(float(scored_instance_val[fraud_label_idx]))

        if fraud_label not in (0, 1):
            err_log.write('{}: Fraud Label \'{}\' invalid.\n'.format(line, fraud_label))
            return None
    except ValueError:
	err_log.write(type(scored_instance_val[fraud_label_idx]) )
        err_log.write('{}: Fraud Label is \'{}\' not an int.\n'.format(line, scored_instance_val[fraud_label_idx]))
        return None

    try:
        # amount should be a numeric value, floating point or not
        amount = float(scored_instance_val[amount_idx])
    except ValueError:
        err_log.write('{}: Amount \'{}\' not a float.\n'.format(line, scored_instance_val[amount_idx]))
        return None

    try:
        # card present label should be either 0 or 1
        cp = int(float(scored_instance_val[cp_idx]))

        if cp not in (0, 1):
            err_log.write('{}: CP/CNP \'{}\' invalid.\n'.format(line, cp))
    except ValueError:
        err_log.write('{}: CP/CNP \'{}\' not an int.\n'.format(line, scored_instance_val[cp_idx]))
        return None

    return [score, fraud_label, amount, cp]

def analyze_scores(scored_instances_loc, delim, score_idx, fraud_label_idx, amount_idx, cp_idx, step_len):
    """
    Analyzes the scoring steps for the scored instances, capturing for each interval:
        * Number of Not Fraud transactions
        * Money in Not Fraud transactions
        * Number of Fraud transactions
        * Money in Fraud transactions
    These metrics are captured for card present and card not present transactions.

    :param scored_instances_loc: location of the file with the scored instances
    :param delim: the delimiter used in the scored instances
    :param score_idx: index of the score column
    :param fraud_label_idx: index of the fraud label column
    :param amount_idx: index of the amount column
    :param cp_idx: index of the cp/cnp label column
    :param step_len: the length of the score step
    :return: the metrics calculated for each step
    """
    scored_instances_file = open(scored_instances_loc, 'r')

    # initialize steps counters, in steps of step_len
    temp_steps_cp = dict()
    temp_steps_cnp = dict()
    for i in xrange(0, 1001, step_len):
        # each step will have counters for the different metrics necessary
        temp_steps_cp[i/step_len] = StepMetrics(i/step_len)
        temp_steps_cnp[i/step_len] = StepMetrics(i/step_len)

    # errors are registered for each line, indicating what was found wrong in the instance
    # when the maximum number of errors is reached, the analysis stops
    line = 0
    errors = 0
    error_log = open("error.log", "w")
    
    for scored_instance in scored_instances_file:
        # instances should be comma separated values
        scored_instance_values = scored_instance.split(delim)

        # relevant data is extracted from the instance
        data = extract_data(scored_instance_values, score_idx, fraud_label_idx, amount_idx, cp_idx, error_log, line)

        # if an error occurred extracting data nothing is done with the instance and after max_errors the analysis stops
        if data is None:
            errors += 1

            if errors >= max_errors:
                error_log.close()
                scored_instances_file.close()

                print "Too many errors occurred, stopping analysis."
                return None
        else:
            # the step this instance belongs is calculated with its score
            step = int(data[0]*1000/step_len)

            # if this instance was fraud
            if is_fraud(data):
                # if this instance is card present
                if is_cp(data):
                    temp_steps_cp[step].fraud_count += 1
                    temp_steps_cp[step].fraud_money += data[2]
                # else is card not present
                else:
                    temp_steps_cnp[step].fraud_count += 1
                    temp_steps_cnp[step].fraud_money += data[2]
            # else is not fraud
            else:
                # if this instance is card present
                if is_cp(data):
                    temp_steps_cp[step].not_fraud_count += 1
                    temp_steps_cp[step].not_fraud_money += data[2]
                # else is card not present
                else:
                    temp_steps_cnp[step].not_fraud_count += 1
                    temp_steps_cnp[step].not_fraud_money += data[2]

        line += 1

    error_log.close()
    scored_instances_file.close()

    return temp_steps_cp.values(), temp_steps_cnp.values()


def write_steps(steps_data, filename, step_len):
    """
    Writes the steps metrics to a file in csv format
    :param steps_data: the steps metrics
    :param filename: the name of the output file
    :param step_len: the length of the score step
    """
    steps_file = open(filename, 'w')
    steps_csv = csv.writer(steps_file)
    for step in steps_data:
        steps_csv.writerow([step.step * step_len, step.not_fraud_count, step.not_fraud_money, step.fraud_count, step.fraud_money])
    steps_file.close()

def calc_steps_all(cp, cnp):
    """
    Sums the metrics from cp and cnp for each step
    :param cp: the metrics for cp in steps
    :param cnp: the metrics for cnp in steps
    :return: the metrics for all in steps
    """
    steps_all_temp = list()
    for step_cp, step_cnp in zip(cp, cnp):
        step_all = StepMetrics(step_cp.step)
        step_all.not_fraud_count = step_cp.not_fraud_count + step_cnp.not_fraud_count
        step_all.not_fraud_money = step_cp.not_fraud_money + step_cnp.not_fraud_money
        step_all.fraud_count = step_cp.fraud_count + step_cnp.fraud_count
        step_all.fraud_money = step_cp.fraud_money + step_cnp.fraud_money
        steps_all_temp.append(step_all)

    return steps_all_temp

def main(argv):
	# reads the arguments passed in the script invocation
	script, scored_instances, prefix, setname, delimiter, score_index, fraud_label_index, amount_index, cp_index, step_len = argv

	# runs the scores analysis for the scored instances
	steps = analyze_scores(scored_instances, delimiter, int(score_index), int(fraud_label_index), int(amount_index), int(cp_index), int(step_len))

	# if the scores analysis was successful, outputs its results
	if steps is not None:
	    #write_steps(steps[0], "steps_cp.csv")
	    #write_steps(steps[1], "steps_cnp.csv")
	    steps_all = calc_steps_all(steps[0], steps[1])
	    write_steps(steps_all, prefix + '_steps_'+setname+'.csv', int(step_len))

	    #metrics_analyzer.metrics_summary(steps[0], 'metrics_summary_cp.txt')
	    #metrics_analyzer.metrics_summary(steps[1], 'metrics_summary_cnp.txt')
	    metrics_analyzer.metrics_summary(steps_all,  prefix + '.'+setname+'out', int(step_len))

	    #metrics_visualizer.metrics_visualize(steps[0], -1, "fig_cp.png")
	    #metrics_visualizer.metrics_visualize(steps[1], -1, "fig_cnp.png")
	    #metrics_visualizer.metrics_visualize(steps_all, -1,  prefix)

if __name__ == "__main__":
    main(sys.argv)

