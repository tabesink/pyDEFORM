import numpy as np
import os
import pandas as pd
from fnmatch import fnmatch


def find_int_between(s, first='_Step', last='.csv'):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return int(s[start:end])
    except ValueError:
        return ""


def get_steps(paths):
    """blah"""

    # process all steps
    # get step values between Step and .csv
    raw_steps = []
    for path in paths:
        raw_steps.append(find_int_between(path))

    # drop duplicate entires
    raw_steps = list(set(raw_steps))
    # print(raw_steps)

    steps = np.array(raw_steps)

    neg_steps = [step for step in steps if step < 0]
    abs_steps = [abs(step) for step in neg_steps]

    # print(neg_steps)
    # print(abs_steps)

    # find closest step value greater than and less than abs_step
    tar_steps = []
    for i, abs_step in enumerate(abs_steps):
        tmp_steps = []

        # get prev step
        val = steps[steps < abs_step].max()
        if val == -1:
            pass
        else:
            tmp_steps.append(val)

        # get current neg step
        tmp_steps.append(neg_steps[i])

        # get next step
        try:
            tmp_steps.append(steps[steps > abs_step].min())
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

    # remove duplicates
    steps = []
    [steps.append(x) for x in tar_steps if x not in steps]

    return steps


def get_centroids(nodes, elements, statevars):
    '''
     dataframe = ProcessCentroid(nodes,elements):

     Input:
       node and element dataframes.

     Output:
       dataframe is dataframe consisting of element centroid coordinates.

     Parses node or element dataframes to calculate element centroid XYZ coordinates.
     Returns a dataframe object
    '''
    nodes = nodes[['X', 'Y', 'Z']]
    elements = elements[['V1', 'V2', 'V3', 'V4']]

    centroids = []
    for i in range(len(elements)):
        # get node ids of element
        pt1 = elements['V1'].iloc[i]
        pt2 = elements['V2'].iloc[i]
        pt3 = elements['V3'].iloc[i]
        pt4 = elements['V4'].iloc[i]

        # get node XYZ coordinates
        nodes.iloc[(pt1 - 1), 0]
        n1 = [nodes.iloc[(pt1 - 1), 0], nodes.iloc[(pt1 - 1), 1], nodes.iloc[(pt1 - 1), 2]]
        n2 = [nodes.iloc[(pt2 - 1), 0], nodes.iloc[(pt2 - 1), 1], nodes.iloc[(pt2 - 1), 2]]
        n3 = [nodes.iloc[(pt3 - 1), 0], nodes.iloc[(pt3 - 1), 1], nodes.iloc[(pt3 - 1), 2]]
        n4 = [nodes.iloc[(pt4 - 1), 0], nodes.iloc[(pt4 - 1), 1], nodes.iloc[(pt4 - 1), 2]]

        # get element volume
        # volume = tet_volume(n1, n2, n3, n4)
        volume = 'n/a'

        # get centroid of element
        cx = (n1[0] + n2[0] + n3[0] + n4[0]) / 4
        cy = (n1[1] + n2[1] + n3[1] + n4[1]) / 4
        cz = (n1[2] + n2[2] + n3[2] + n4[2]) / 4

        centroids.append([i + 1, volume, cx, cy, cz])  # (i+1, offeset start of element number from 0 to 1)

    # create dataframe from node_data list
    pcd = pd.DataFrame(centroids, columns=['Element Id', 'Element Volume', 'CX', 'CY', 'CZ'])  # ignoring element volume for backtracking algorithm
    merged_pcd = pcd.merge(statevars, how='left', on='Element Id')
    return merged_pcd


def run(path):
    """Create point cloud files"""
    print('***********************************\n* CREATE POINT CLOUDS\n***********************************')

    rz_paths, elmcon_paths, effs_paths = [], [], []

    # loop through files in folder
    for path, subdirs, files in os.walk(path):
        for name in files:
            if 'RZ' in name:
                rz_paths.append(os.path.join(path, name))
            elif 'ELMCON' in name:
                elmcon_paths.append(os.path.join(path, name))
            else:
                effs_paths.append(os.path.join(path, name))

    # get ordered list of steps
    steps = get_steps(rz_paths)
    print(' \nProcessing element centroids...')

    # create pcds for every step
    for step in steps:
        print('  Step{}'.format(str(step)))

        # load dataframes
        elements = pd.read_csv(os.path.join(path, 'ELMCON_Step' + str(step) + '.csv'))
        nodes = pd.read_csv(os.path.join(path, 'RZ_Step' + str(step) + '.csv'))
        statevars = pd.read_csv(os.path.join(path, 'STRAIN_Step' + str(step) + '.csv'))

        # create pcd and save to database path
        pcd = get_centroids(nodes, elements, statevars)
        pcd.to_csv(os.path.join(path, 'PCD_Step' + str(step) + '.csv'), index=False)


if __name__ == "__main__":

    # path configs
    database_path = os.path.join(os.getcwd(), 'playground', '_metadata')  # _metadata folder path containing parsed step data

    run(database_path)
