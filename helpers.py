from pathlib import Path
from importlib.util import find_spec
import time, pickle
from configparser import ConfigParser
 
def config(filename='etc/database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
 
    # get section, default to postgresql
    db = {}
    
    # Checks to see if section (postgresql) parser exists
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
         
    # Returns an error if a parameter is called that is not listed in the initialization file
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
 
    return db

def get_path(folder, file):
    '''Package path. __init__ required'''
    return Path(*find_spec(folder).submodule_search_locations) / file

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