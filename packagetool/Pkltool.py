import pickle


def read(path):
    with open(path, "rb") as f:
        dicts = pickle.load(f)
        return dicts


def write(path, pkl):
    with open(path, "wb") as f:
        pickle.dump(pkl, f)
