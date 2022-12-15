#!/usr/bin/env python3
import logging
import argparse
from pathlib import Path

from job import Job, JobError
from utils import get_config, date_to_filename, date_from_filename, save_activity_log

__all__ = ['get_region_map']

def get_activity_id(function_name, function_callargs):
	return '%s.%s' % (function_name, date_to_filename(function_callargs['date']))

@save_activity_log(get_activity_id)
def get_region_map(date, segmentation_map, stat_images, config):
	'''Execute the SPoCA get_ch_map or get_ar_map program on a segmentation map to create a region map'''
	
	logging.info('Creating a region map for segmentation map %s', segmentation_map)
	
	region_map = Path(config.get('output_file').format(date = date_to_filename(date)))
	
	region_map.parent.mkdir(exist_ok=True)
	
	job = Job(
		config.get('executable'),
		positional_parameters = [segmentation_map] + [image for (name, image) in stat_images.items() if image is not None],
		optional_parameters = {
			'config' : config.get('config_file'),
			'output': region_map
		}
	)
	
	exit_code, output, error = job.execute()
	
	# Check if the job ran succesfully
	if exit_code != 0:
		raise JobError(config.get('executable'), exit_code, output, error, segmentation_map = segmentation_map, stat_images = stat_images)
	
	# Check if the region map was actually created
	if region_map.is_file():
		logging.info('Wrote region map "%s"', region_map)
	else:
		raise JobError(config.get('executable'), exit_code, output, error, message = 'Job was successful but region map {region_map} is missing', region_map = region_map)
	
	return region_map


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_region_map.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--stat-image', '-i', metavar = ('NAME', 'FILEPATH'), nargs = 2, action = 'append', default = [], help = 'The name and path to an image FITS files for which to compute statistics')
	parser.add_argument('segmentation_map', metavar = 'FILEPATH', help = 'The path to a segmentation map')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_log.output_directory = config.get('LOGGING', 'output_directory')
	
	try:
		region_map = get_region_map(date_from_filename(args.segmentation_map), args.segmentation_map, dict(args.stat_image), config['GET_REGION_MAP'])
	except Exception as why:
		logging.exception('Could not create region map for segmentation map %s: %s', args.segmentation_map, why)
