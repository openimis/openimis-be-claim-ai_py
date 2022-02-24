import os
import pickle
from pathlib import Path

from django.conf import settings


def load_from_assembly_file(path, load_func=pickle.load):
    isabs = os.path.isabs(path)
    if not isabs:
        # openimis-be_py
        base = Path(settings.BASE_DIR).parent
        path = F'{base}/{path}'

    with open(path, 'rb') as f:
        return load_func(f)
