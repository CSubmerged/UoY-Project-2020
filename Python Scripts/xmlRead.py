"""
The tripinfo files store the vehicular time loss for each vehicle.
These files need to be parsed, summed and outputted in order to collect results.
This script helps output these values.
"""
from xml.dom import minidom


def read_single_tripinfo_file(filename):
    mydoc = minidom.parse(filename)

    items = mydoc.getElementsByTagName('tripinfo')

    total_timeloss = 0
    for elem in items:
        total_timeloss += float(elem.attributes['timeLoss'].value)

    # print('Total Timeloss =', total_timeloss)
    return total_timeloss


# print("Baseline - Total Time loss:",
#       read_single_tripinfo_file('ResultsBaseline/tripinfo.Jul26.Baseline.xml'))
#
# print("Control Eastbound - Total Time loss:",
#       read_single_tripinfo_file('ResultsControl/tripinfo.Jul26.ControlEastbound.xml'))
# print("Control Westbound - Total Time loss:",
#       read_single_tripinfo_file('ResultsControl/tripinfo.Jul26.ControlWestbound.xml'))


def read_multiple_tripinfo_files(periods, thresholds, folder_prefix):
    for period in periods:
        for threshold in thresholds:
            file_code = 'P' + str(period) + '-T' + str(threshold)
            tripinfo = "tripinfo.Jul26." + file_code + ".xml"
            if folder_prefix:
                filename = folder_prefix + tripinfo
            else:
                filename = tripinfo
            print(file_code, '- Total Time Loss:', read_single_tripinfo_file(filename))


# print("*** Results 1 ***")
# read_multiple_tripinfo_files([1, 2, 5, 10, 30, 60, 300, 600], [0, 1, 2, 5, 10], "Results1/")
#
# print("*** Results 2 ***")
# read_multiple_tripinfo_files([1, 2, 5, 10, 30, 60, 300, 600], [0.25, 0.5, 0.75, 1.5], "Results2/")
#
# print("*** Results 3 ***")
# read_multiple_tripinfo_files([5], [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9], "Results3a/")
# read_multiple_tripinfo_files([6, 7, 8, 9], [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "Results3b/")
# read_multiple_tripinfo_files([10], [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9], "Results3a/")
# read_multiple_tripinfo_files([11, 12, 13, 14, 15], [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], "Results3b/")

