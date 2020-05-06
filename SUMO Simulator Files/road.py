import os, sys
from sumolib import checkBinary
import traci


def edit_lane(action: str, direction: str, lane_no: int):
    left_lane = "left_"
    right_lane = "right_"

    if action == 'open':
        vehicle_classes = ['passenger']
    elif action == 'close':
        vehicle_classes = []
    else:
        raise ValueError('Open/Close not defined for editLane')

    if direction == "both":
        left_lane += str(lane_no - 1)
        traci.lane.setAllowed(left_lane, vehicle_classes)
        right_lane += str(lane_no - 1)
        traci.lane.setAllowed(right_lane, vehicle_classes)

    else:
        if direction == 'left':
            lane = left_lane + str(lane_no - 1)
        elif direction == "right":
            lane = right_lane + str(lane_no - 1)
        traci.lane.setAllowed(lane, vehicle_classes)


# Direction can be 'left', 'right' or 'both'
def open_lane(direction: str, lane_no: int):
    edit_lane('open', direction, lane_no)


def open_lanes(direction: str, lane_nos: list):
    for lane_no in lane_nos:
        open_lane(direction, lane_no)


def close_lane(direction: str, lane_no: int):
    edit_lane('close', direction, lane_no)


def close_lanes(direction: str, lane_nos: list):
    for lane_no in lane_nos:
        close_lane(direction, lane_no)


def cars_in_lane(direction: str, lane_no: int):
    lookup = direction + "_" + str(lane_no - 1)
    return traci.lane.getLastStepVehicleNumber(lookup)


def reverse_lane(step: int, lane_status: [int, int], direction: str, lane_no=0):
    # Changes the direction of lane given. If no lane is given, automatically choose the innermost lane

    numerical_direction = 0 if direction == 'left' else 1
    opposite_direction = 'right' if direction == 'left' else 'left'

    if lane_no == 0:
        lane_no = lane_status[numerical_direction]

    # Ensure that correct lane is the one being swapped
    if direction == "left" and lane_status[0] != lane_no or \
            direction == "right" and lane_status[1] != lane_no:
        raise AttributeError('Attempted to change direction of a non-central lane')

    close_lane(direction, lane_no)

    # Wait until no cars now going the wrong way are in the lane
    while cars_in_lane(direction, lane_no) > 0:
        step += 1
        traci.simulationStep()

    # Update the lane status
    lane_status = (lane_status[0] - 1 if direction == 'left' else lane_status[0] + 1,
                   lane_status[1] - 1 if direction == 'right' else lane_status[1] + 1)

    lane_to_open = lane_status[1 - numerical_direction]  # Gets status of the opposite to the numerical direction
    open_lane(opposite_direction, lane_to_open)

    return step, lane_status


def run(period, threshold, filecode, disable_lane_changing=False, favoured_direction="Eastbound"):
    """execute the TraCI control loop"""

    # Setup available lanes for a 3 lane road layout
    open_lanes('both', [1, 2])
    if disable_lane_changing and favoured_direction == "Baseline":
        # Don't close any lanes, baseline test runs with all 4 lanes open
        lane_status = (2, 2)
    elif disable_lane_changing and favoured_direction == "Westbound":
        # Only the control tests use westbound as the starting direction
        close_lane('right', 2)
        lane_status = (2, 1)
    else:
        close_lane('left', 2)
        lane_status = (1, 2)

    # Prepare variables used in main execution loop
    step = 0
    internal_period = 0
    right_sum = 0
    left_sum = 0
    no_lane_reversals = 0
    reversal_time = 0

    # Main Simulation Execution Control Loop
    while traci.simulation.getMinExpectedNumber() > 0:
        # If lane changing is disable (eg for control case), skip lane changing algorithm
        if not disable_lane_changing:
            # Traffic Density: Get the number of vehicles on each feeder road, and add to the total
            left_start_num = traci.edge.getLastStepVehicleNumber('left_start')
            right_start_num = traci.edge.getLastStepVehicleNumber('right_start')
            left_sum += left_start_num
            right_sum += right_start_num

            if internal_period == period:
                # As period has been reached, check whether lanes should swap
                entry_step = step
                if left_sum/period > right_sum/period + threshold and lane_status[0] == 1:
                    step, lane_status = reverse_lane(step, lane_status, 'right')
                    no_lane_reversals += 1
                    reversal_time += (step - entry_step)
                elif right_sum/period > left_sum/period + threshold and lane_status[1] == 1:
                    step, lane_status = reverse_lane(step, lane_status, 'left')
                    no_lane_reversals += 1
                    reversal_time += (step - entry_step)

                # Reset variables
                internal_period = 0
                left_sum = 0
                right_sum = 0

        # Move the simulation one step forward
        traci.simulationStep()
        step += 1
        internal_period += 1

    # Output the tracked variables to a consolesummary file
    filename = 'consolesummary.Jul27.' + filecode + '.txt'
    with open(filename, 'w') as f:
        print('Final simulation time step:', step, file=f)
        print('Number of lane reversals:', no_lane_reversals, file=f)
        if no_lane_reversals > 0:
            print('Total & Mean reversal duration:', reversal_time, reversal_time/no_lane_reversals, file=f)

    traci.close()
    sys.stdout.flush()


def execute_and_log_simulation(period, threshold, disable_lane_changing=False, favoured_direction="Eastbound"):
    if disable_lane_changing:
        if favoured_direction == "Baseline":
            file_code = "Baseline"
        else:
            file_code = 'Control' + favoured_direction
    else:
        file_code = 'P' + str(period) + '-T' + str(threshold)

    summary = "summary.Jul26." + file_code + ".xml"
    tripinfo = "tripinfo.Jul26." + file_code + ".xml"

    # Sumo is started as a subprocess and then the python script connects and runs
    traci.start([sumoBinary, "-c", "road.sumocfg",
                 "--summary", summary,
                 "--tripinfo-output", tripinfo,
                 "--start", "true",
                 "--quit-on-end", "true"])
    run(period, threshold, file_code, disable_lane_changing, favoured_direction)


# Functions to run the various experiments used in the project:
def run_baseline_experiment():
    period = 0
    threshold = 0
    disable_lane_changing = True
    execute_and_log_simulation(period, threshold, disable_lane_changing, "Baseline")


def run_experiment1():
    for period in [1, 2, 5, 10, 30, 60, 300, 600]:
        for threshold in [0, 1, 2, 5, 10]:
            print("Running test: Period", period, "& Threshold", threshold)
            execute_and_log_simulation(period, threshold)


def run_control_experiment():
    period = 0
    threshold = 0
    disable_lane_changing = True
    for direction in ["Eastbound", "Westbound"]:
        print("Running test: Direction", direction)
        execute_and_log_simulation(period, threshold, disable_lane_changing, direction)


def run_experiment2():
    for period in [1, 2, 5, 10, 30, 60, 300, 600]:
        for threshold in [0, 0.25, 0.5, 0.75, 1, 1.5, 2]:
            print("Running test: Period", period, "& Threshold", threshold)
            execute_and_log_simulation(period, threshold)


def run_experiment3():
    for period in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
        for threshold in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
            print("Running test: Period", period, "& Threshold", threshold)
            execute_and_log_simulation(period, threshold)


if __name__ == "__main__":

    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    sumoBinary = checkBinary('sumo-gui')

    # If the script is being run as standard, execute a basic example to show
    # how the simulator runs
    period = 14
    threshold = 0.3

    traci.start([sumoBinary, "-c", "road.sumocfg"])
    run(period, threshold, "ExampleTest.P1-T0")
