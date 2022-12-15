#!/usr/bin/env python3
import logging
import argparse
from pathlib import Path

from job import Job, JobError
from utils import get_config, date_to_filename, date_from_filename, save_activity_log

__all__ = ['get_overlay_image']

def get_activity_id(function_name, function_callargs):
	return '%s.%s' % (function_name, date_to_filename(function_callargs['date']))

@save_activity_log(get_activity_id)
def get_overlay_image(date, map, background_image, config):
	'''Execute the SPoCA overlay program on a region map to display the contours of the regions on top of an image FITS file'''
	
	logging.info('Creating overlay image for map %s', map)
	
	overlay_image = Path(config.get('output_file').format(date = date_to_filename(date)))
	
	overlay_image.parent.mkdir(exist_ok=True)
	
	job = Job(
		config.get('executable'),
		positional_parameters = [map, background_image],
		optional_parameters = {
			'config' : config.get('config_file'),
			'output': overlay_image
		}
	)
	
	exit_code, output, error = job.execute()
	
	# Check if the job ran succesfully
	if exit_code != 0:
		raise JobError(config.get('executable'), exit_code, output, error, map = map, background_image = background_image)
	
	# Check if the map was actually created
	if overlay_image.is_file():
		logging.info('Wrote overlay image "%s"', overlay_image)
	else:
		raise JobError(config.get('executable'), exit_code, output, error, message = 'Job was successful but map {map} is missing', overlay_image = overlay_image)
	
	return overlay_image


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_overlay_image.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('region_map', metavar = 'FILEPATH', help = 'The path to a region map')
	parser.add_argument('background_image', metavar = 'FILEPATH', help = 'The path to an image FITS file for the background')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_log.output_directory = config.get('LOGGING', 'output_directory')
	
	try:
		overlay_image = get_overlay_image(date_from_filename(args.region_map), args.region_map, args.background_image, config['GET_OVERLAY_IMAGE'])
	except Exception as why:
		logging.exception('Could not create overlay image for region map %s: %s', args.region_map, why)
