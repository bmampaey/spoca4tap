#!/usr/bin/env python3
import logging
import argparse
from pathlib import Path

# HACK to make sure that the SPoCA script are found
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import get_config, date_to_filename, date_from_filename, save_activity_provenance
from SPoCA.scripts.clean_map_of_shortlived_regions import clean_map
from get_longlived_regions_colors import read_regions_colors

__all__ = ['get_cleaned_map']

def get_activity_id(function_name, function_callargs):
	return '%s.%s' % (function_name, date_to_filename(function_callargs['date']))

@save_activity_provenance(get_activity_id)
def get_cleaned_map(date, region_map, longlived_regions_colors, config):
	'''Clean a region map to only keep the long lived regions'''
	
	cleaned_map = Path(config.get('output_file').format(date = date_to_filename(date)))
	
	cleaned_map.parent.mkdir(exist_ok=True)
	
	return clean_map(region_map, config.get('image_hdu_name'), cleaned_map, longlived_regions_colors)

# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_cleaned_map.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--regions-colors', '-r', metavar = 'FILEPATH', default = 'longlived_regions_colors.txt', help = 'The path to a file with the list of regions color numbers to keep (default is longlived_regions_colors.txt)')
	parser.add_argument('region_map', metavar = 'FILEPATH', help = 'The path to a region map')
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_provenance.output_directory = config.get('PROVENANCE', 'output_directory')
	
	try:
		longlived_regions_colors = read_regions_colors(args.regions_colors)
	except Exception as why:
		logging.exception('Could not read regions colors from file %s: %s', args.regions_colors, why)
	else:
		try:
			cleaned_map = get_cleaned_map(date_from_filename(args.region_map), args.region_map, longlived_regions_colors, config['LIFESPAN_CLEANING'])
		except Exception as why:
			logging.exception('Could not create cleaned map for region map %s: %s', args.region_map, why)
