"""
 Read DEFORM .db data (ELEMCON, RZ, STRAIN) in DEF_REPORT; save step data to .csv files
 Author: tabesink
 License: n/a
 Source: n/a
<<<<<<< HEAD

 Update:
    1/5/2022    v0.0.1 - completed code block; logging not supported
=======
>>>>>>> df1ed5380e88bc89c9817cddb2adaad649496eb9
"""
import sys
import os
import shutil
import pandas as pd
from fnmatch import fnmatch
from exceptions import *
from utils import *


def get_files(path):
    """
     check simulation folder and get key file paths
    """
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

            if fnmatch(name, rz_file):
                rz_path = os.path.join(path, name)

            if fnmatch(name, effs_file):
                effs_path = os.path.join(path, name)

    return elmcon_path, rz_path, effs_path


<<<<<<< HEAD
def save_step_file(step_data, step, database_path, file_type=None):
    """ save data to .csv file"""
    # specify data content type
    if file_type == 'RZ':
        dataframe = pd.DataFrame(step_data, columns=['Node Id', 'X', 'Y', 'Z'])
        dataframe.to_csv(os.path.join(database_path, file_type + '_' + step + '.csv'), index=False)
    elif file_type == 'ELMCON':
        dataframe = pd.DataFrame(step_data, columns=['Element Id', 'V1', 'V2', 'V3', 'V4'])
        dataframe.to_csv(os.path.join(database_path, file_type + '_' + step + '.csv'), index=False)
    else:
        # special case: inital steps do not exhibit strain; .csv file will have empty rows
        dataframe = pd.DataFrame(step_data, columns=['Element Id', 'Eff-Strain'])
        dataframe.to_csv(os.path.join(database_path, file_type + '_' + step + '.csv'), index=False)


def read_file(path, database_path, file_type=None):
    """seperate data in main file and save independent step files"""
=======
def save_step_file(node_data, step, database_path, file_type='RZ'):
    """ save data to .csv file"""
    dataframe = pd.DataFrame(node_data, columns=['Node Id', 'X', 'Y', 'Z'])
    dataframe.to_csv(os.path.join(database_path, file_type + '_' + step + '.csv'), index=False)


def read_file(path, database_path):
    """read data files and return step list"""
>>>>>>> df1ed5380e88bc89c9817cddb2adaad649496eb9

    # open file
    file = open(path)
    data_content = [i.strip().split() for i in file.readlines()]
    file.close()

<<<<<<< HEAD
    # inits
    # tmp_counter = 0 # FOR DEBUGGING
    step_data = []
    clip_data = False  # False: if white space is read, signal start of step; True: if white space is read, signal end of step

    # loop through data content
    for i in range(len(data_content)):
        line = data_content[i]

        # check cases
        if not line:                                                        # case 1: white space
            if clip_data == False:
                clip_data = True
            else:
                # specify data content type
                if 'RZ' in path:
                    file_type = 'RZ'
                elif 'ELMCON' in path:
                    file_type = 'ELMCON'
                else:
                    file_type = 'STRAIN'

                # save data to temp folder
                save_step_file(step_data, step, database_path, file_type=file_type)

                """
                # FOR DEBUGGING
                tmp_counter += 1
                if tmp_counter == 3:
                    break
                else:
                    continue
                """

                # intialize vars for next simulation step
                step_data = []
                clip_data = False

        elif 'Step' in line[1]:                                             # case 2: * Step -1
            # get step number
            step = ''.join(line[1:])
            print('  {}'.format(step))

        elif any(char in line[0] for char in ['RZ', 'ELMCON', 'STRAIN']):   # case 3: RZ           1   32271
            # skip line
            pass

        else:                                                               # case 4: relevant data
            # store relevant data in list
            if 'RZ' in path:
                idx, x, y, z = line
                step_data.append((int(idx), float(x), float(y), float(z)))
            elif 'ELMCON' in path:
                idx, v1, v2, v3, v4 = data_content[i]
                step_data.append((int(idx), int(v1), int(v2), int(v3), int(v4)))
            else:
                idx, eff_strain = data_content[i]
                step_data.append((int(idx), float(eff_strain)))
=======
    # seperate data in main file and save into independent step files
    if 'RZ' in path:

        # loop through data content
        tmp_counter = 0
        step = ''
        node_data = []
        clip_data = False
        for i in range(len(data_content)):
            line = data_content[i]

            # check cases
            if not line:                                            # case 1: white space
                if clip_data == False:
                    clip_data = True  # clip data content when next white space is read (signals end of step)
                else:
                    # save node data to temp folder
                    save_step_file(node_data, step, database_path)

                    tmp_counter += 1
                    if tmp_counter == 1:
                        break
                    else:
                        continue
                    # intialize vars for next simulation step
                    step = ''
                    node_data = []
                    clip_data = False  # (signals start of step)
            elif 'Step' in line[1]:                                 # case 2: * Step -1
                # get step number
                step = step.join(line[1:])
                print('  Processing node data: {}'.format(step))
            elif 'RZ' in line[0]:                                   # case 3: RZ           1   32271
                # skip line
                pass
            else:                                                   # case 4: relevant data
                # store relevant data in list
                idx, x, y, z = line
                node_data.append((int(idx), float(x), float(y), float(z)))
>>>>>>> df1ed5380e88bc89c9817cddb2adaad649496eb9


def create_folder(path, name='_metadata'):
    """if folder name exists in root path, delete folder; else create fodler"""
    path = os.path.join(path, name)
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        shutil.rmtree(path)
        os.mkdir(path)
    return path


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
<<<<<<< HEAD
    print('***********************************\n* PARSING STEP DATA\n***********************************')
=======
    print('Processing data...')
>>>>>>> df1ed5380e88bc89c9817cddb2adaad649496eb9

    # create folder to store temp data
    database_path = create_folder(cwd)

<<<<<<< HEAD
    # read data file; save step data
    print('\n Processing element data...')
    read_file(elmcon_path, database_path, file_type='ELMCON')

    print('\n Processing node data...')
    read_file(rz_path, database_path, file_type='RZ')

    print('\n Processing strain data...')
    read_file(effs_path, database_path, file_type='STRAIN')
=======
    # read data file
    read_file(rz_path, database_path)
>>>>>>> df1ed5380e88bc89c9817cddb2adaad649496eb9


if __name__ == "__main__":

    # path configs
    cwd = os.path.join(os.getcwd(), 'playground')  # root folder path
    simulation_path = os.path.join(cwd, 'dataset')  # temp location of DEF_REPORT of simulation .db
    simulation_name = 'test'

    run(cwd, simulation_path, simulation_name)
