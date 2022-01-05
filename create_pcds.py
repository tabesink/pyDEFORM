import numpy as np
import os
import pandas as pd
from fnmatch import fnmatch

# check key file pattern
    elmcon_file = "MetalFlow_ELMCON.txt"
    rz_file = "MetalFlow_RZ.txt"
    effs_file = "StateVar__Strain.txt"

    elmcon_path, rz_path, effs_path = None, None, None

    # loop through files in folder
    for path, subdirs, files in os.walk(path):
        for name in files:
            if fnmatch(name, elmcon_file):
                elmcon_path = os.path.join(path, name)


def get_target_steps(fpath_lst):

    # process all steps
    # get step values between Step and .DAT
    raw_steps = []
    for fpath in fpath_lst:
        raw_steps.append(find_int_between(fpath))

    # drop duplicate entires
    raw_steps = list(set(raw_steps))

    step_lst = np.array(raw_steps)

    neg_steps = [step for step in step_lst if step < 0]
    abs_steps = [abs(step) for step in neg_steps]

    # find closest step value greater than and less than abs_step
    tar_steps = []
    for i, abs_step in enumerate(abs_steps):
        tmp_steps = []

        # get prev step
        val = step_lst[step_lst < abs_step].max()
        if val == -1:
            pass
        else:
            tmp_steps.append(step_lst[step_lst < abs_step].max())

        # get current neg step
        tmp_steps.append(neg_steps[i])

        # get next step
        try:
            tmp_steps.append(step_lst[step_lst > abs_step].min())
        except:
            pass
        tar_steps.append(tmp_steps)

    # process target steps
    tar_steps = sum(tar_steps, [])
    neg_steps = [step for step in tar_steps if step < 0]
    abs_steps = sorted([abs(step) for step in tar_steps])

    # replace steps in tar_steps with with corresponding remeshing steps (-*)
    for step in neg_steps:
        idx = abs_steps.index(abs(step))
        abs_steps[idx] = step

    tar_steps = abs_steps

    return tar_steps


def run(cwd, simulation_path, simulation_name):
    # check for file paths
    try:
        elmcon_path, rz_path, effs_path = get_files(simulation_path)
        if None in (elmcon_path, rz_path, effs_path):
            raise MissingDEFREPORT
    except MissingDEFREPORT:
        print('Generate DEF_REPORT')
        sys.exit(1)

    # process data files
    print('***********************************\n* CREATING POINTCLOUD FILES\n***********************************')


if __name__ == "__main__":

    # path configs
    cwd = os.path.join(os.getcwd(), 'playground')  # root folder path
    simulation_path = os.path.join(cwd, 'dataset')  # temp location of DEF_REPORT of simulation .db
    simulation_name = 'test'

    run(cwd, simulation_path, simulation_name)
