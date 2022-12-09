#!/usr/bin/env python3
import logging
import argparse
from pathlib import Path

from job import Job, JobError
from utils import get_config, date_to_filename, date_from_filename, save_activity_provenance

__all__ = ['get_segmentation_map']


def get_activity_id(function_name, function_callargs):
	return '%s.%s' % (function_name, date_to_filename(function_callargs['date']))

@save_activity_provenance(get_activity_id)
def get_segmentation_map(date, images, config):
	'''Execute the SPoCA attribution program on image FITS files to create a segmentation map'''
	
	logging.info('Creating segmentation map for date %s', date.isoformat())
	
	centers_file = Path(config.get('centers_file').format(date = date_to_filename(date)))
	
	if not centers_file.is_file():
		raise ValueError('Centers file %s not found' % centers_file)
	
	segmentation_map = Path(config.get('output_file').format(date = date_to_filename(date)))
	
	segmentation_map.parent.mkdir(exist_ok=True)
	
	job = Job(
		config.get('executable'),
		positional_parameters = images,
		optional_parameters = {
			'config' : config.get('config_file'),
			'centersFile' : centers_file,
			'output': segmentation_map
		}
	)
	
	exit_code, output, error = job.execute()
	
	# Check if the job ran succesfully
	if exit_code != 0:
		raise JobError(config.get('executable'), exit_code, output, error, images = images, centers_file = centers_file)
	
	# Check if the segmentation map was actually created
	if segmentation_map.is_file():
		logging.info('Wrote segmentation map "%s"', segmentation_map)
	else:
		raise JobError(config.get('executable'), exit_code, output, error, message = 'Job was successful but segmentation map {segmentation_map} is missing', segmentation_map = segmentation_map)
	
	return segmentation_map


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_segmentation_map.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('images', metavar = 'FILEPATH', nargs = '+', help = 'The path to an image FITS file')

	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_provenance.output_directory = config.get('PROVENANCE', 'output_directory')
	
	try:
		segmentation_map = get_segmentation_map(date_from_filename(args.images[0]), args.images, config['GET_SEGMENTATION_MAP'])
	except Exception as why:
		logging.exception('Could not create segmentation map for images %s: %s', args.images, why)
