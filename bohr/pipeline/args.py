import argparse

_heuristic_args = None

def get_heuristic_args():
    return _heuristic_args


def parse_heuristic_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('task', type=str)

    parser.add_argument('--issues-file', type=str, default=None)
    parser.add_argument('--changes-file', type=str, default=None)
    parser.add_argument('--commits-file', type=str, required=True)
    parser.add_argument('--n-parallel', type=int, default=5)
    parser.add_argument('--n-commits', type=int, default=None)
    parser.add_argument('--profile', action='store_true', default=False)

    global _heuristic_args
    _heuristic_args = parser.parse_args()

    return _heuristic_args
