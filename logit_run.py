import numpy as np

from sklearn.linear_model import LogisticRegression


import timeit
import os, requests

save_dir="./files"


def train_and_predict(uid, jobid, url_list: list):
    """

    :param uid:
    :param jobid:
    :param url_list: [X_train_url, y_train_url, X_test_url]
    :return:
    """

    np_path_list = [uid + "_" + jobid + "_" + "X_train" + ".npz",
                     uid + "_" + jobid + "_" + "X_test" + ".npz",
                     uid + "_" + jobid + "_" + "y_train" + ".npz"]


    for u in range(len(url_list)):
        f_path = os.path.join(save_dir, np_path_list[u])
        if os.path.exists(f_path):
            os.remove(f_path)

        res = requests.get(url_list[u])
        with open(f_path, "wb") as f:
            f.write(res.content)

    t0 = timeit.default_timer()

    lr = LogisticRegression(
        penalty="l2",
        max_iter=1000
    )

    X_train = np.load(os.path.join(save_dir, np_path_list[0]))["arr_0"]
    y_train = np.load(os.path.join(save_dir, np_path_list[1]))["arr_0"]
    X_test = np.load(os.path.join(save_dir, np_path_list[2]))["arr_0"]

    lr.fit(X_train, y_train)

    y_pred = lr.predict(X_test)
    y_pred_path = os.path.join(save_dir, uid + "_" + jobid + "_" + "y_predict" + ".npz")
    if os.path.exists(y_pred_path):
        os.remove(y_pred_path)
    np.savez(y_pred_path, y_pred)

    run_time = timeit.default_timer() - t0

    return {"y_pred_path": y_pred_path, "run_time": run_time}



