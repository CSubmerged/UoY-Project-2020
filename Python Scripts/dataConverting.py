"""
The data from Highways England WebTRIS system is given in csv files.
These data files when downloaded should be checked to ensure they have been split properly,
as ones I used needed to be fixed.
"""
import os, sys, csv
from datetime import datetime


def output_flow_str(direction: str, iteration: int, start_time: int, end_time: int, number: int):
    flow_str = '<flow type="car" departLane="free" departSpeed="max" departPos="0" '
    if direction == "eastbound":
        flow_str += ('id="w2e' + str(iteration) + '" from="right_start" to="right_end" ')
    elif direction == "westbound":
        flow_str += ('id="e2w' + str(iteration) + '" from="left_start" to="left_end" ')
    else:
        raise ValueError("Direction not given to output_flow")
    flow_str += 'begin="' + str(start_time) + \
                '" end="' + str(end_time) + \
                '" number="' + str(number) + '"/>\n'

    return flow_str


def generate_accurate_flow(direction, iteration, date, time_interval, volume):
    # Work out seconds from start time
    start_date = datetime(2019, 1, 1)
    datetime_object = datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
    date_diff = datetime_object - start_date
    ms = date_diff.days * 86400

    # use time interval (should be every 15 mins) to add appropriate time
    ms += int(time_interval) * 900

    return output_flow_str(direction, iteration, ms, ms + 899, int(volume))


def generate_flow(direction, iteration, volume):
    # Data is listed in 15 mins intervals, so if data is missing it can just be skipped.
    time = iteration * 900
    return output_flow_str(direction, iteration, time, time + 899, int(volume))


def import_csv_data(filename: str, direction: str):
    flow_matrix = []
    average_speed_sum = 0
    speed_count = 0
    month_iteration = 0
    with open(filename, newline='') as csvfile:
        csv_file = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in csv_file:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                date = row[1]
                datetime_object = datetime.strptime(date, '%d/%m/%Y %H:%M')
                time_period_ending = row[2]
                time_interval = row[3]
                av_speed = row[22]
                volume = row[23]
                if volume != '' and int(volume) >= 0:
                    # To obtain just the results for the 26th July, pick out data from that specific day
                    if datetime_object.month == 7 and datetime_object.day == 26:
                        # flow = generate_flow(direction, line_count - 1, volume)
                        flow = generate_flow(direction, month_iteration, volume)
                        flow_matrix.append(flow)
                        month_iteration += 1
                    if av_speed != '':
                        average_speed_sum += int(av_speed)
                        speed_count += 1
                else:
                    print(date, time_interval, "is missing data")

                line_count += 1

        print(f'Processed {line_count} lines.')
        print('average speed =', average_speed_sum / speed_count)

    return flow_matrix


def find_busy_month(filename: str, direction: str):
    month_index = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
                   7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}

    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in spamreader:
            if line_count == 0:
                # Skip column names
                line_count += 1
            else:
                date = row[1]
                datetime_object = datetime.strptime(date, '%d/%m/%Y %H:%M')
                volume = row[23]
                if volume != '' and int(volume) >= 0:
                    month_index[datetime_object.month] += int(volume)

                line_count += 1

        print(f'Processed {line_count} lines.')
        print('Months:', sorted(month_index.items(), key=lambda x: x[1]))

    return


def find_busy_day(filename: str, direction: str):
    day_index = {}

    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        line_count = 0
        for row in spamreader:
            if line_count == 0:
                # Skip column names
                line_count += 1
            else:
                date = row[1]
                datetime_object = datetime.strptime(date, '%d/%m/%Y %H:%M')
                strdate = str(datetime_object.day) + '/' + str(datetime_object.month)
                volume = row[23]
                if volume != '' and int(volume) >= 0:
                    if strdate in day_index.keys():
                        day_index[strdate] += int(volume)
                    else:
                        day_index[strdate] = int(volume)

                line_count += 1

        print(f'Processed {line_count} lines.')
        print('days:', sorted(day_index.items(), key=lambda x: x[1], reverse=True))

    return


def convert_data():
    # Import the Southbound data to represent the eastbound direction in the simulator
    data_east = import_csv_data('Daily0fixed.csv', "eastbound")
    print('done', len(data_east))

    # Write the output flow xml to a txt file for now
    fe = open('2e 26 Jul - A556 Southbound.txt', "w+")
    fe.writelines(data_east)
    fe.close()

    # Import the Northbound data to represent the westbound direction in the simulator
    data_west = import_csv_data('Daily1fixed.csv', "westbound")
    print('done', len(data_west))

    # Write the output flow xml to a txt file for now
    fw = open('2w 26 Jul - A556 Northbound.txt', "w+")
    fw.writelines(data_west)
    fw.close()


def combine_txt():
    # Combine the two directional text files to form another that can be inserted into
    # a rou.xml file for SUMO to use
    output = open('A556-26 Jul.txt', 'w')
    f1 = open('2e 26 Jul - A556 Southbound.txt', "r")
    f2 = open('2w 26 Jul - A556 Northbound.txt', "r")
    e = f1.readline()
    w = f2.readline()
    while e:
        output.write(e)
        output.write(w)
        e = f1.readline()
        w = f2.readline()
    f1.close()
    f2.close()
    output.close()


# Use these to run the functions defined above:
# find_busy_month('Daily0fixed.csv', "eastbound")
# find_busy_month('Daily1fixed.csv', "westbound")

# find_busy_day('Daily0fixed.csv', "eastbound")
# find_busy_day('Daily1fixed.csv', "westbound")

# convert_data()

# combine_txt()
