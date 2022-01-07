import numpy as np
import os
import pandas as pd
from sklearn.neighbors import BallTree


def find_int_between(s, first='PCD_Step', last='.csv'):
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


def get_nearest(pcd_tminus, pcd_tplus, k_neighbors=1):
    """
     Find nearest neighbors for all ct_tminus centroids (source points) from a set of ct_tplus centroids (candidate points)
    """
    # get mesh centroids
    ct_tminus = pcd_tminus  # source points
    cx, cy, cz = ct_tminus['CX'].values.tolist(), ct_tminus['CY'].values.tolist(), ct_tminus['CZ'].values.tolist()
    ct_tminus_arr = np.array([[cx[i], cy[i], cz[i]] for i in range(len(cx))])  # point list of lists

    ct_tplus = pcd_tplus  # candidate points
    cx, cy, cz = ct_tplus['CX'].values.tolist(), ct_tplus['CY'].values.tolist(), ct_tplus['CZ'].values.tolist()
    ct_tplus_arr = np.array([[cx[i], cy[i], cz[i]] for i in range(len(cx))])

    # create tree from the candidate points
    tree = BallTree(ct_tplus_arr, leaf_size=2)

    # find closest points and distances
    distances, indices = tree.query(ct_tminus_arr, k=k_neighbors)

    # transpose to get distances and indices into arrays
    distances = distances.transpose()
    indices = indices.transpose()

    # get closest indices and distances (i.e. array at index 0)
    # note: for the second closest points, you would take index 1, etc.
    closest = indices[0]
    closest_dist = distances[0]

    # return indices and distances
    return (closest, closest_dist)


def interpolate_statevars(pcd_tminus, pcd_tplus):

    # get closest point index of pcd_tminus to points in pcd_tplus
    closest_idx, _ = get_nearest(pcd_tminus, pcd_tplus, k_neighbors=1)

    # get list of state vars from pcd_tplus
    statevar_lst = list(pcd_tplus['Eff-Strain'])
    interpolated_statevar_lst = [statevar_lst[idx] for idx in closest_idx]

    # pass interpolated_strain_lst into pcd_tminus
    pcd_tminus['Eff-Strain'] = interpolated_statevar_lst

    return pcd_tminus


def backtrack_statevars(path, steps):
    """backtrack statevar data from final sim. step to initial sim. step"""

    def _load_pcd(path, step):
        """load pcd dataframe"""
        return pd.read_csv((os.path.join(path, 'PCD_Step' + str(step) + '.csv')))

    def _save_pcd(pcd, path, step):
        """save tracked pcd dataframe"""
        pcd.to_csv(os.path.join(path, 'TRACKED_PCD_Step' + str(step) + '.csv'), index=False)

    # start statevar backtrack loop
    for i in range(1, len(steps) + 1):

        if i == 1:
            # get mesh object at last simul. step
            step_tplus = steps[-1]
            pcd_tplus = _load_pcd(path, step_tplus)

        else:
            # load mesh files in reverse
            step_tminus = steps[-1 * i]
            pcd_tminus = _load_pcd(path, step_tminus)

            # interpolattion between mesh object logic
            if step_tplus < 0 and step_tminus > 0:
                # cond1 ex.: step_tplus = -223 ; step_tminus = 222
                # map statvars from mesh at step_tplus to mesh at step_tminus
                # track back statevars for next iteration
                step_tplus = step_tminus
                pcd_tplus = interpolate_statevars(pcd_tminus, pcd_tplus)

            elif step_tplus > 0 and step_tminus < 0:
                # cond2 ex.: step_tplus = 220 ; step_tminus = -217
                # map statvars from meshobj at step_tminus to meshobj at step_tplus to
                # pass vars to next iteration
                pcd_tplus = interpolate_statevars(pcd_tminus, pcd_tplus)
                step_tplus = step_tminus

            else:
                # cond3 ex.: step_tminus = 222 and step_tplus = 220

                # replace statevars of pcd_tminus with pcd_tplus
                statevar_lst = list(pcd_tplus['Eff-Strain'])
                pcd_tminus['Eff-Strain'] = statevar_lst

                # pass vars to next iteration
                step_tplus = step_tminus
                pcd_tplus = pcd_tminus

        # save tracked pcd
        _save_pcd(pcd_tplus, path, step_tplus)
        print('Back tracking statevar data through step {}'.format(step_tplus))
    return pcd_tplus


def run(path):
    """Backtrack state vars """
    print('***********************************\n* BACKTRACK MESH STATE\n***********************************')

    # get steps
    pcd_paths = []

    # loop through files in folder
    for path, subdirs, files in os.walk(path):
        for name in files:
            if 'PCD' in name:
                pcd_paths.append(os.path.join(path, name))

    # get ordered list of steps
    steps = get_steps(pcd_paths)

    # get tracked mesh
    tracked_mesh = backtrack_statevars(path, steps)  # returns inital mesh with backtracked state vars, intial mesh and final mesh


if __name__ == "__main__":
    # path configs
    database_path = os.path.join(os.getcwd(), 'playground', '_metadata')  # _metadata folder path containing parsed step data

    run(database_path)
