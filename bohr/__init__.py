from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / 'data'
TEST_DIR = DATA_DIR / 'test'
TRAIN_DIR = DATA_DIR / 'train'
HEURISTIC_DIR = PROJECT_DIR / 'bohr' / 'heuristics'
