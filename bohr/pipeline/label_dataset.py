import numpy as np
import pandas as pd
from snorkel.labeling.model import LabelModel

from bohr import PROJECT_DIR
from bohr import params
from bohr.core import load_labeling_functions


def label_dataset(args):
    heuristic_groups = "_".join(args.heuristic_groups)
    df = pd.read_csv(args.commits_file)

    L_train = np.load(PROJECT_DIR / 'generated' / params.TASK / 'heuristic_matrix_train.pkl', allow_pickle=True)

    print(L_train.shape)
    print(df.shape)

    lfs = load_labeling_functions({params.TASK})

    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(L_train=L_train, n_epochs=100, log_freq=100, seed=123)

    labels, probs = label_model.predict(L=L_train, return_probs=True)
    df_labeled = df.assign(bug=labels)

    df_probs = pd.DataFrame(probs, columns=['prob_bugless', 'prob_bug'])
    df_labeled = pd.concat([df_labeled, df_probs], axis=1)

    if params.LABEL_DATASET_DEBUG:
        df_lfs = pd.DataFrame(L_train, columns=[lf.name for lf in lfs])
        for name, col in df_lfs.iteritems():
            df_lfs[name] = col.map({0: name, 1: name, -1: ''})
        col_lfs = df_lfs.apply(lambda c: ';'.join([v for v in c if v]), axis=1)
        df_labeled['lfs'] = col_lfs

    df_labeled.to_csv(params.LABELED_DATASET_OUTPUT_PATH, index=False)


if __name__ == '__main__':
    label_dataset()
