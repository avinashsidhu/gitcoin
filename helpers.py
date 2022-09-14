from pathlib import Path
from importlib.util import find_spec
import time, pickle
import yaml
from dateutil import parser

class ToDictMixin:
    def to_dict(self, varlist=[]):
        if not varlist:
            properties = self._get_properties()
            varlist = {**self.__dict__, **properties}
        return {
            prop: self._represent(value)
            for prop, value in varlist.items()
            if not self._is_internal(prop)
        }
    def _get_properties(self):
        properties = {}
        for p in dir(self):
            try:
                is_property = isinstance(getattr(type(self),p), property)
            except AttributeError:
                continue
            if is_property:
                properties[p] = getattr(self, p)
        return properties
    def _represent(self, value):
        if isinstance(value, object):
            if hasattr(value, 'to_dict'):
                return value.to_dict()
            else:
                return str(value)
        else:
            return value
    def _is_internal(self, prop):
        return prop.startswith('_')


def to_date(x):
    return parser.isoparse(x).replace(tzinfo=None).date() if x else None

def to_float(x):
    return float(x) if x else None

def to_int(x):
    return int(x) if x else int()

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