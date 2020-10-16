import argparse

_heuristic_args = None

def get_heuristic_args():
    return _heuristic_args


def parse_heuristic_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('heuristic_groups', nargs='+')
    parser.add_argument('--save-heuristics-matrix-train-to',
                        default='heuristic_matrix_train.pkl')
    parser.add_argument('--save-heuristics-matrix-herzig-to',
                        default='heuristic_matrix_herzig.pkl')
    parser.add_argument('--save-heuristics-matrix-berger-to',
                        default='heuristic_matrix_berger.pkl')
    parser.add_argument('--save-heuristics-matrix-1151-commits-to',
                        default='heuristic_matrix_1151_commits.pkl')

    parser.add_argument('--issues-file', type=str, default=None)
    parser.add_argument('--changes-file', type=str, default=None)
    parser.add_argument('--commits-file', type=str, required=True)
    parser.add_argument('--save-metrics-to', default='heuristic_metrics.json')
    parser.add_argument('--n-parallel', type=int, default=5)
    parser.add_argument('--n-commits', type=int, default=None)
    parser.add_argument('--profile', action='store_true', default=False)

    global _heuristic_args
    _heuristic_args = parser.parse_args()

    return _heuristic_args
