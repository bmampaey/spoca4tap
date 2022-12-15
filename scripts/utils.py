#!/usr/bin/env python3
import re
import inspect
import json
import configparser
from datetime import datetime
import git
from pandas import DataFrame, Timedelta
from pathlib import Path
from urllib.parse import urljoin
from functools import wraps


__all__ = ['date_range', 'get_config', 'date_to_filename', 'date_from_filename', 'get_url', 'get_commit_version', 'write_tap_parameters_to_csv', 'save_activity_log']

def date_range(start, end, step):
	'''Equivalent to range for date'''
	date = start.replace()
	while date < end:
		yield date
		date += step

# ConfigParser converter for list of int from comma separated values
# to allow parsing list of wavelengths or quality bits
# (allows for random spaces e.g "1, 2,3  " will give [1,2,3])
def getintlist(value):
	return [int(i) for i in value.split(',')]

def get_config(config_file):
	'''Parse a ini config file'''
	config = configparser.ConfigParser(converters = {
		'intlist': getintlist,
		'timedelta': Timedelta,
	})
	config.read(config_file)
	return config

def date_to_filename(date):
	'''Return a date formated for inclusion in a file name'''
	return date.strftime('%Y%m%d_%H%M%S')

def date_from_filename(filename):
	'''Extract a date from a file name as formated by date_to_filename'''
	match = re.search('\d{8}_\d{6}', str(filename))
	if match is None:
		raise ValueError('No date found in file name %s' % filename)
	else:
		return datetime.strptime(match[0], '%Y%m%d_%H%M%S')

def get_url(filepath, base_url, base_dir = None):
	'''Convert a file path to a URL'''
	if filepath is None:
		return None
	path = Path(filepath).absolute()
	relative_path = path.relative_to(base_dir or path.parent)
	return urljoin(base_url, str(relative_path))

def get_commit_version(path):
	'''Return the commit version of the file specified in path'''
	repo = git.Repo(path, search_parent_directories=True)
	return repo.head.object.hexsha

def write_tap_parameters_to_csv(records, filepath):
	'''Write a CSV file with the records'''
	Path(filepath).parent.mkdir(exist_ok = True)
	DataFrame.from_records(records).to_csv(filepath, index = False)

def save_activity_log(get_activity_id):
	'''Decorator for a function that will record every call to a function and the call arguments to a JSON file to create provenance documentation'''
	
	def json_encoder(value):
		if isinstance(value, configparser.SectionProxy):
			return dict(value)
		elif isinstance(value, datetime):
			return value.isoformat()
		elif isinstance(value, Path):
			return str(value)
		elif isinstance(value, set):
			return list(value)
		else:
			return value
	
	def decorator(function):
		
		@wraps(function)
		def wrapper(*args, **kwargs):
			output_directory = Path(save_activity_log.output_directory)
			output_directory.mkdir(exist_ok = True)
			
			function_output = function(*args, **kwargs)
			
			function_callargs = inspect.getcallargs(function, *args, **kwargs)
			activity_id = get_activity_id(function.__name__, function_callargs)
			activity_info = {
				'activity_id': activity_id,
				'function_name': function.__name__,
				'function_commit': get_commit_version(inspect.getfile(function)),
				'function_callargs': function_callargs,
				'function_output': function_output,
				'function_docstring' : inspect.getdoc(function)
			}
			with open(output_directory / (activity_id + '.json'), 'wt') as file:
				json.dump(activity_info, file, indent = 3, default = json_encoder )
			
			return function_output
		
		return wrapper
	
	return decorator

save_activity_log.output_directory = './activity_log'
