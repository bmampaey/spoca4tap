#!/usr/bin/env python3
import logging
import argparse
from datetime import datetime
from astropy.io import fits

from get_longlived_regions_colors import read_regions_colors
from utils import write_tap_parameters_to_csv

__all__ = ['get_tracking_tap_parameters_from_file']

TRACKING_HDU_NAME = 'TrackingRelations'

def get_tracking_tap_parameters_from_file(tracked_map, regions_colors = None):
	'''Extract the TAP parameters for the tracking table'''
	
	with fits.open(tracked_map) as hdulist:
		return get_tracking_tap_parameters_from_tracking_hdu(hdulist[TRACKING_HDU_NAME], regions_colors)


def get_tracking_tap_parameters_from_tracking_hdu(hdu, regions_colors = None):
	'''Extract the TAP parameters from a FITS BinTableHDU of tracking relations'''
	tap_parameters = list()
	
	for tracking_relation in hdu.data:
		past_color = int(tracking_relation['PAST_COLOR'])
		present_color = int(tracking_relation['PRESENT_COLOR'])
		
		if regions_colors is not None:
			if past_color not in regions_colors:
				logging.debug('Skipping tracking relation with past color %s', past_color)
				continue
			if present_color not in regions_colors:
				logging.debug('Skipping tracking relation with present color %s', present_color)
				continue
		
		tap_parameters.append({
			'previous': 'spoca_coronalhole_{tracked_color}_{date_obs}'.format(tracked_color = past_color, date_obs = datetime.fromisoformat(tracking_relation['PAST_DATE_OBS']).strftime('%Y%m%d_%H%M%S')), # e.g. spoca_coronalhole_198_20100112_160000
			'next': 'spoca_coronalhole_{tracked_color}_{date_obs}'.format(tracked_color = present_color, date_obs = datetime.fromisoformat(tracking_relation['PRESENT_DATE_OBS']).strftime('%Y%m%d_%H%M%S')), # e.g. spoca_coronalhole_198_20100112_160000
			'overlap_area_projected': float(tracking_relation['OVERLAP_AREA_PROJECTED']),
			'overlap_area_pixels': float(tracking_relation['OVERLAP_NUMBER_PIXELS']),
		})
	
	return tap_parameters


# Start point of the script

if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_tracking_tap_parameters_from_file.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--output', '-o', default = 'rob_spoca_ch.tracking.csv', help = 'The file path for the output CSV file (default is rob_spoca_ch.tracking.csv)')
	parser.add_argument('--regions-colors', '-r', metavar = 'FILEPATH', help = 'An optional file path to a list of region color numbers (1 per line) to extract parameters for; if not provided, all regions will be used')
	parser.add_argument('tracked_map', metavar = 'FILEPATH', help = 'The file path to a tracked SPoCA CH map FITS file')
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	if args.regions_colors:
		try:
			regions_colors = read_regions_colors(args.regions_colors)
		except Exception as why:
			logging.exception('Could not read region colors from file %s: %s', args.regions_colors, why)
			raise
	else:
		regions_colors = None
	
	try:
		tap_parameters = get_tracking_tap_parameters_from_file(args.tracked_map, regions_colors)
	except Exception as why:
		logging.exception('Could not extract TAP parameters for file %s: %s', args.tracked_map, why)
		raise
	
	try:
		write_tap_parameters_to_csv(tap_parameters, args.output)
	except Exception as why:
		logging.exception('Error while writing CSV file %s : %s', args.output, why)
		raise
