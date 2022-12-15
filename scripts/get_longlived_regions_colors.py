#!/usr/bin/env python3
import logging
import argparse
import pandas

# HACK to make sure that the SPoCA script are found
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_config, date_to_filename, date_from_filename, save_activity_log
from SPoCA.scripts.aggregate_tables_from_fits import get_dataframe_from_files
from SPoCA.scripts.write_regions_lifespan_to_csv import get_regions_lifespan_by_color

__all__ = ['get_longlived_regions_colors', 'read_regions_colors', 'write_regions_colors']

def get_activity_id(function_name, function_callargs):
	return '%s.%s-%s' % (function_name, date_to_filename(date_from_filename(function_callargs['region_maps'][0])), date_to_filename(date_from_filename(function_callargs['region_maps'][-1])))

@save_activity_log(get_activity_id)
def get_longlived_regions_colors(region_maps, config):
	'''Compute the lifespan of regions on tracked region maps and create the list of longlived regions colors'''
	
	logging.info('Extracting info from regions maps')
	
	regions_dataframe = get_dataframe_from_files(region_maps, config.get('region_hdu_name'))
	regions_dataframe['FIRST_DATE_OBS'] = pandas.to_datetime(regions_dataframe['FIRST_DATE_OBS'])
	regions_dataframe['DATE_OBS'] = pandas.to_datetime(regions_dataframe['DATE_OBS'])
	
	logging.info('Computing regions lifespan')
	regions_lifespan_dataframe = get_regions_lifespan_by_color(regions_dataframe)
	
	logging.info('Selecting regions with a lifespan larger than %s', config.get('min_lifespan'))
	regions_lifespan_dataframe = regions_lifespan_dataframe.loc[regions_lifespan_dataframe['LIFESPAN'] >= config.gettimedelta('min_lifespan')]
	
	# The index is the TRACKED_COLOR column
	return set(regions_lifespan_dataframe.index)


def read_regions_colors(filepath):
	'''Read a list of regions colors from a text file'''
	with open(filepath, 'rt') as file:
		regions_colors = [int(color) for color in file.read().split()]
	return regions_colors


def write_regions_colors(regions_colors, filepath):
	'''Write a list of regions colors to a text file'''
	with open(filepath, 'wt') as file:
		file.write('\n'.join(str(color) for color in regions_colors))


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_longlived_regions_colors.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--output', '-o', default = 'longlived_regions_colors.txt', help = 'The file path for the output text file (default is longlived_regions_colors.txt)')
	parser.add_argument('region_maps', metavar = 'FILEPATH', nargs = '+', help = 'The path to a tracked region map')
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_log.output_directory = config.get('LOGGING', 'output_directory')
	
	# Extract the colors of the longlived regions
	try:
		longlived_regions_colors = get_longlived_regions_colors(args.region_maps, config['LIFESPAN_CLEANING'])
	except Exception as why:
		logging.exception('Error getting longlived regions colors from maps : %s', why)
	else:
		try:
			write_regions_colors(longlived_regions_colors, args.output)
		except Exception as why:
			logging.exception('Error while writing regions colors file %s : %s', args.output, why)
		else:
			logging.info('Wrote longlived region colors to file %s', args.output)
