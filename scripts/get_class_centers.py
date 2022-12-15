#!/usr/bin/env python3
import logging
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from sdo_data import SdoData
from job import Job, JobError
from utils import date_range, get_config, date_to_filename, save_activity_log

__all__ = ['get_class_centers']

def get_activity_id(function_name, function_callargs):
	return '%s.%s' % (function_name, date_to_filename(function_callargs['date']))

@save_activity_log(get_activity_id)
def get_class_centers(date, images, config):
	'''Execute the SPoCA classification program on image FITS files to compute the class centers'''
	
	logging.info('Computing class centers for date %s', date.isoformat())
	
	class_centers_file = Path(config.get('output_file').format(date = date_to_filename(date)))
	
	class_centers_file.parent.mkdir(exist_ok=True)
	
	job = Job(
		config.get('executable'),
		positional_parameters = images,
		optional_parameters = {
			'config' : config.get('config_file'),
			'centersFile' : class_centers_file
		}
	)
	
	exit_code, output, error = job.execute()
	
	# Check if the job ran succesfully
	if exit_code != 0:
		raise JobError(config.get('executable'), exit_code, output, error, images = images, class_centers_file = class_centers_file)
	
	# Check if the class centers file was actually created
	if class_centers_file.is_file():
		logging.info('Wrote class centers file "%s"', class_centers_file)
	else:
		raise JobError(config.get('executable'), exit_code, output, error, message = 'Job was successful but centers file {class_centers_file} is missing', class_centers_file = class_centers_file)
	
	return class_centers_file


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_class_centers.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--start-date', '-s', required = True, type = datetime.fromisoformat, help = 'Start date of AIA files (ISO 8601 format)')
	parser.add_argument('--end-date', '-e', default = datetime.utcnow(), type = datetime.fromisoformat, help = 'End date of AIA files (ISO 8601 format)')
	parser.add_argument('--interval', '-i', default = 6, type = int, help = 'Number of hours between two results')

	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_log.output_directory = config.get('LOGGING', 'output_directory')
	
	aia_data = SdoData(
		file_pattern = config.get('AIA_DATA', 'file_pattern'),
		hdu_name_or_index = config.getint('AIA_DATA', 'hdu_index'),
		ignore_quality_bits = config.getintlist('AIA_DATA', 'ignore_quality_bits'),
	)
	
	for date in date_range(args.start_date, args.end_date, timedelta(hours=args.interval)):
		images = [aia_data.get_good_quality_file(date = date, wavelength = wavelength) for wavelength in config.getintlist('GET_CLASS_CENTERS', 'aia_wavelengths')]
		if None in images:
			logging.info('Image missing for date %s, cannot compute class centers', date.isoformat())
		else:
			try:
				class_centers_file = get_class_centers(date, images, config['GET_CLASS_CENTERS'])
			except Exception as why:
				logging.exception('Could not compute class centers for date %s: %s', date.isoformat(), why)
