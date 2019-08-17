'''
functions to deal with params
'''
# built-in
import os
import pickle
from collections import ChainMap

# external

# original
from upsample.utils import loggings

logger = loggings.get_standard_logger(__name__)

def get_config_path(model_dir, config_name='config'):
    '''
    returns path for the config file
    '''
    path = os.path.join(model_dir, config_name)
    return path

def is_config_available(target_dir):
    """
    this function checks if there is a config file in
    the specified directory.
    """
    return os.path.exists(get_config_path(target_dir))

def load_config(
        directory,
        name='config',
        default=None,
        relax_set=None,
        validate=True,
        logger=logger,
):
    '''
    this file will load a config
    from config file stored in specified directory

    Args:
        directory: (str) model directory
        name: (str) the name of the config file
        default: (dict) default config
            Required only when validate=True.
        relax_set: (list) the list of strings
            which might be contained in the config as a key.
            this will relax the validation.
        validate: (bool) whether this func validates the retrieved config
            The validation will be conducted by the comparison of
            default config and the retrieved config
    '''
    if is_config_available(directory):
        logger.info("config file found in {}".format(directory))
        with open(os.path.join(directory, name), 'rb') as f:
            params_temp = pickle.load(f)
    else:
        logger.info('config file not found in {}'.format(directory))
        return None

    if validate:
        if default is None:
            logger.error('default config is not provided...')
            return None
        elif config_validator(params_temp, default, relax_set):
            logger.info("params in config file confirmed to be valid")
            params = params_temp
        else:
            logger.info('params was invalid')
            return None
    else:
        logger.warn('params is not validated')
        params = params_temp
    return params

def config_validator(config_test, config_ground_truth, relax_set=None):
    """
    this function checks if the given config is valid or not
    using config_ground_truth
    returns true if a config is valid

    Args:
        config_test: config object which will be tested
        config_ground_truth: default config object
        relax_set: a set of keys for a config that can be relaxed,
            which means even if config_test doesnt have a key which is
            included in relax_set, this func will still judge it fine.
    """
    test_key = set(config_test.keys())
    ground_truth_key = set(config_ground_truth.keys())

    if relax_set is not None:
        relax_set = set(relax_set)
        test_key = test_key.union(relax_set)
        ground_truth_key = ground_truth_key.union(relax_set)

    return test_key.issubset(ground_truth_key)

def merge_params(*dicts):
    '''
    this func will merge dicts.
    should be useful for templating
    '''
    dicts = list(filter(lambda x: x is not None, dicts))
    combined = ChainMap(*dicts)
    return dict(combined)

def save_config(file_target, params, exclude_list=None):
    '''
    this func will save a paramters
    into a file
    '''
    directory = get_directory(file_target)
    if not os.path.exists(directory):
        recursive_mkdir(directory)

    params = dict(params)
    params_cp = deepcopy(params)
    if exclude_list is not None:
        for key in exclude_list:
            del params_cp[key]

    with open(file_target, 'wb') as f:
        pickle.dump(params_cp, f)
    return

