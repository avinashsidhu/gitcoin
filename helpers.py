from pathlib import Path
from importlib.util import find_spec
import datetime, time, pickle
import yaml
from dateutil import parser
 
def convert_type(self, varlist: list, method: object):
    for var in varlist:
        value = method(getattr(self, var))
        setattr(self, var, value)
convert_to_date = lambda x: parser.isoparse(x).replace(tzinfo=None) if x else None
convert_to_float = lambda x: float(x) if x else None

def get_path(folder, file):
    '''Package path. __init__ required'''
    path = Path(*find_spec(folder).submodule_search_locations) / file
    path.touch(exist_ok=True)
    return path

def timer(func):
    def wrapper(*args, **kwargs):
        t_start = time.time()
        result = func(*args, **kwargs)
        t_total = time.time() - t_start
        print(f'{func.__name__} took {t_total:.2f}s')
        return result
    return wrapper

def trim(ser):
    return ser.apply(lambda x: x.strip())

# make it subclass of Dataframe (df.save_pickle())
def save_pickle(data, folder, file):
    with get_path(folder, file).open('wb') as f:
        pickle.dump(data, f)

def config(section: str=None, filename='etc/config.yaml'):
    with open(filename, 'r') as f:
        if section:
            config = yaml.safe_load(f)[section]
        else:
            config = yaml.safe_load(f)
    return config