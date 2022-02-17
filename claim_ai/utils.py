import os
import pickle
from pathlib import Path


def load_from_module_file(path, load_func=pickle.load):
    isabs = os.path.isabs(path)
    if not isabs:
        abs_path = Path(__file__).absolute().parent.parent  # path to claim_ai module folder
        path = F'{abs_path}/{path}'

    with open(path, 'rb') as f:
        return load_func(f)
