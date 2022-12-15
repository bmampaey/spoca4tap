#!/usr/bin/env python3
import logging
import argparse

from job import Job, JobError
from utils import get_config, date_to_filename, date_from_filename, save_activity_log

__all__ = ['get_tracked_map']

def get_activity_id(function_name, function_callargs):
	return '%s.%s-%s' % (function_name, date_to_filename(date_from_filename(function_callargs['untracked_maps'][0])), date_to_filename(date_from_filename(function_callargs['untracked_maps'][-1])))

@save_activity_log(get_activity_id)
def get_tracked_map(tracked_maps, untracked_maps, config):
	'''Execute the SPoCA tracking program on region maps'''
	
	logging.info('Running tracking on region maps %s', untracked_maps)
	
	job = Job(
		config.get('executable'),
		positional_parameters = tracked_maps + untracked_maps,
		optional_parameters = {
			'config' : config.get('config_file')
		}
	)
	
	exit_code, output, error = job.execute()
	
	# Check if the job ran succesfully
	if exit_code != 0:
		raise JobError(config.get('executable'), exit_code, output, error, untracked_maps = untracked_maps)
	

# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_tracked_map.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--tracked-map', metavar = 'FILEPATH', action = 'append', default = [], help = 'The path to a previously tracked region map to establish tracking relations with the past')
	parser.add_argument('untracked_maps', metavar = 'FILEPATH', nargs = '+', help = 'The path to an untracked region map')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_log.output_directory = config.get('LOGGING', 'output_directory')
	
	try:
		get_tracked_map(args.tracked_map, args.untracked_maps, config['GET_TRACKED_MAP'])
	except Exception as why:
		logging.exception('Could not execute tracking: %s', why)
