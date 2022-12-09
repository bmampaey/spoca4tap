#!/usr/bin/env python3
import os
import logging
import argparse
from datetime import datetime
from astropy import units
from astropy.io import fits
from sunpy.map import Map
from sunpy.coordinates import frames

from get_longlived_regions_colors import read_regions_colors
from utils import get_config, get_url, write_tap_parameters_to_csv

__all__ = ['get_epn_core_tap_parameters_from_file']


IMAGE_HDU_NAME = 'CoronalHoleMap'
REGIONS_HDU_NAME = 'Regions'
REGIONS_STATS_AIA_HDU_NAME = 'AIA_193_CoronalHoleStats'
REGIONS_STATS_HMI_HDU_NAME = 'HMI_MAGNETOGRAM_CoronalHoleStats'
WAVELENGTH = 193 * units.angstrom
STAT_AIA_IMAGE_TEMPLATE = 'SDO/AIA 193Å {date_obs} level2'
STAT_HMI_IMAGE_TEMPLATE = 'SDO/HMI magnetogram {date_obs} level1.5'


FIX_TAP_PARAMETERS = {
	'dataproduct_type': 'ci',
	'target_name': 'Sun',
	'target_class': 'Star',
	'spectral_range_min': WAVELENGTH.to(units.hertz, equivalencies = units.spectral()).value,
	'spectral_range_max': WAVELENGTH.to(units.hertz, equivalencies = units.spectral()).value,
	'spatial_frame_type': 'celestial',
	'instrument_host_name': 'Solar Dynamics Observatory#SDO',
	'instrument_name': 'Atmospheric Imaging Assembly#AIA',
	'processing_level': 5,
	'processing_level_desc': 'CODMAC (Derived Data Record)',
	'service_title': 'ROB SPoCA-CH',
	'access_format': 'application/fits',
	'target_region': 'solar-corona',
	'feature_name': 'coronal hole',
	'publisher': 'Royal Observatory of Belgium',
	'spatial_coordinate_description': 'HPC',
	'spatial_origin': 'HELIOCENTER',
	'time_scale': 'UTC',
}


def get_epn_core_tap_parameters_from_file(tracked_map, cleaned_map, overlay_image, regions_colors, config):
	'''Extract the TAP parameters for the epn_core table'''
	file_date = datetime.fromtimestamp(os.path.getmtime(cleaned_map))
	file_size = os.path.getsize(cleaned_map) * units.byte
	
	file_parameters = {
		'creation_date': file_date.isoformat(),
		'release_date': file_date.isoformat(),
		'modification_date': file_date.isoformat(),
		'access_url': get_url(cleaned_map, config.get('map_base_url'), config.get('map_base_dir', None)),
		'access_estsize': round(file_size.to(units.kilobyte).value), # MUST be an integer TODO this must be the size of the cleaned map
		'thumbnail_url': get_url(overlay_image, config.get('map_overlay_base_url'), config.get('map_overlay_base_dir', None)),
		'datalink_url': '',  # TODO
	}
	
	with fits.open(tracked_map) as hdulist:
		
		try:
			image_hdu = hdulist[IMAGE_HDU_NAME]
			map = Map(image_hdu.data, image_hdu.header)
		except Exception as why:
			logging.error('Could not create Sunpy Map from file %s: %s', tracked_map, why)
			raise
		
		map_parameters = get_epn_core_tap_parameters_from_map(map)
		
		# The parameters from regions are mandatory, raise exception in case of error
		try:
			regions_parameters = get_epn_core_tap_parameters_from_regions_hdu(hdulist[REGIONS_HDU_NAME], map, regions_colors)
		except Exception as why:
			logging.error('Could not extract TAP parameters for regions from file %s: %s', tracked_map, why)
			raise
		
		# The parameters from regions stats are NOT mandatory, just log a warning
		try:
			regions_stats_aia_parameters = get_epn_core_tap_parameters_from_regions_stats_hdu(hdulist[REGIONS_STATS_AIA_HDU_NAME], STAT_AIA_IMAGE_TEMPLATE, prefix = 'ch_stat_aia_')
		except Exception as why:
			logging.warning('Could not extract TAP parameters for AIA regions stats from file %s: %s', tracked_map, why)
			regions_stats_aia_parameters = dict()
		
		try:
			regions_stats_hmi_parameters = get_epn_core_tap_parameters_from_regions_stats_hdu(hdulist[REGIONS_STATS_HMI_HDU_NAME], STAT_HMI_IMAGE_TEMPLATE, prefix = 'ch_stat_hmi_')
		except Exception as why:
			logging.warning('Could not extract TAP parameters for HMI regions stats from file %s: %s', tracked_map, why)
			regions_stats_hmi_parameters = dict()
	
	tap_parameters = list()
	for id, region_parameters in regions_parameters.items():
		tap_parameters.append({
			**FIX_TAP_PARAMETERS,
			**file_parameters,
			**map_parameters,
			**region_parameters,
			**regions_stats_aia_parameters.get(id, {}),
			**regions_stats_hmi_parameters.get(id, {}),
		})
	
	return tap_parameters

def get_epn_core_tap_parameters_from_map(map):
	'''Extract the TAP parameters from a a sunpy Map'''
	return {
		'obs_id': 'aia_193_{date_obs}'.format(date_obs = map.date.strftime('%Y%m%d_%H%M%S')), # e.g. aia_193_20100112_160000
		'time_min': map.date.jd, # Map date is an astopy time.Time, convert the date to Julian
		'time_max': map.date.jd,
		'target_distance_min': map.dsun.to(units.kilometer).value, # spacecraft-target distance in km
		'target_distance_max': map.dsun.to(units.kilometer).value,
		'observer_lon': map.heliographic_longitude.to(units.degree).value, # spacecratf position in degrees
		'observer_lat': map.heliographic_latitude.to(units.degree).value,
	}


def get_epn_core_tap_parameters_from_regions_hdu(hdu, map, regions_colors = None):
	'''Extract the TAP parameters from a FITS BinTableHDU of regions'''
	tap_parameters = dict()
	
	for region in hdu.data:
		tracked_color = int(region['TRACKED_COLOR'])
		
		if regions_colors is not None and tracked_color not in regions_colors:
			logging.debug('Skipping region with tracked color %s', tracked_color)
			continue
		
		date_obs = datetime.fromisoformat(region['DATE_OBS'])
		boxmin_ra, boxmin_dec = pixel2hpc(map, region['XBOXMIN'], region['YBOXMIN'])
		boxmax_ra, boxmax_dec = pixel2hpc(map, region['XBOXMAX'], region['YBOXMAX'])
		center_ra, center_dec = pixel2hpc(map, region['XCENTER'], region['YCENTER'])
		
		tap_parameters[region['ID']] = {
			'granule_uid': 'spoca_coronalhole_{tracked_color}_{date_obs}'.format(tracked_color = tracked_color, date_obs = date_obs.strftime('%Y%m%d_%H%M%S')), # e.g. spoca_coronalhole_198_20100112_160000
			'granule_gid': 'spoca_coronalhole_{tracked_color}'.format(tracked_color = tracked_color), # e.g spoca_coronalhole_198
			'c1min': boxmin_ra.to(units.degree).value,
			'c1max': boxmax_ra.to(units.degree).value,
			'c2min': boxmin_dec.to(units.degree).value,
			'c2max': boxmax_dec.to(units.degree).value,
			'ch_c1_centroid': center_ra.to(units.degree).value,
			'ch_c2_centroid': center_dec.to(units.degree).value,
			'ch_area_projected': float(region['AREA_PROJECTED']),
			'ch_area_projected_error': float(region['AREA_PROJECTED_UNCERTAINITY']),
			'ch_area_deprojected': float(region['AREA_DEPROJECTED']) * 1000000, # The value in the table is in Mm² but it must be provided in km²
			'ch_area_deprojected_error': float(region['AREA_DEPROJECTED_UNCERTAINITY'])* 1000000, # The value in the table is in Mm² but it must be provided in km²
			'ch_area_pixels': int(region['NUMBER_PIXELS']),
		}
	
	return tap_parameters


def get_epn_core_tap_parameters_from_regions_stats_hdu(hdu, image_template, prefix):
	'''Extract the TAP parameters from a FITS BinTableHDU of region statistics'''
	tap_parameters = dict()
	
	image = image_template.format(date_obs = hdu.header['DATE-OBS'].split('.')[0] + 'Z')
	
	for region_stats in hdu.data:
		tap_parameters[region_stats['ID']] = {
			prefix + 'image': image,
			prefix + 'sample_size': int(region_stats['NUMBER_GOOD_PIXELS']),
			prefix + 'min': float(region_stats['MIN_INTENSITY']),
			prefix + 'max': float(region_stats['MAX_INTENSITY']),
			prefix + 'mean': float(region_stats['MEAN_INTENSITY']),
			prefix + 'median': float(region_stats['MEDIAN_INTENSITY']),
			prefix + 'variance': float(region_stats['VARIANCE']),
			prefix + 'skewness': float(region_stats['SKEWNESS']),
			prefix + 'kurtosis': float(region_stats['KURTOSIS']),
			prefix + 'median': float(region_stats['MEDIAN_INTENSITY']),
			prefix + 'first_quartile': float(region_stats['LOWERQUARTILE_INTENSITY']),
			prefix + 'third_quartile': float(region_stats['UPPERQUARTILE_INTENSITY']),
		}
	
	return tap_parameters


def pixel2hpc(map, x, y):
	# Convert the pixel coordinates to world coordinates
	world = map.pixel_to_world(x * units.pixel, y * units.pixel)
	hpc = world.transform_to(frames.Helioprojective)
	return hpc.Tx, hpc.Ty


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_epn_core_tap_parameters_from_file.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--regions-colors', '-r', metavar = 'FILEPATH', help = 'An optional file path to a list of region color numbers (1 per line) to extract parameters for; if not provided, all regions will be used')
	parser.add_argument('--output', '-o', default = 'rob_spoca_ch.epn_core.csv', help = 'The file path for the output CSV file (default is rob_spoca_ch.epn_core.csv)')
	parser.add_argument('tracked_map', metavar = 'FILEPATH', help = 'The file path to a tracked SPoCA CH map FITS file')
	parser.add_argument('cleaned_map', metavar = 'FILEPATH', help = 'The file path to a cleaned SPoCA CH map FITS file')
	parser.add_argument('overlay_image', metavar = 'FILEPATH', nargs = '?', help = 'The file path to the overlay image of the cleaned SPoCA CH map')
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	if args.regions_colors:
		try:
			regions_colors = read_regions_colors(args.regions_colors)
		except Exception as why:
			logging.exception('Could not read region colors from file %s: %s', args.regions_colors, why)
			raise
	else:
		regions_colors = None
	
	try:
		tap_parameters = get_epn_core_tap_parameters_from_file(args.tracked_map, args.cleaned_map, args.overlay_image, regions_colors, config['TAP_PARAMETERS'])
	except Exception as why:
		logging.exception('Could not extract TAP parameters for file %s: %s', args.tracked_map, why)
		raise
	
	try:
		write_tap_parameters_to_csv(tap_parameters, args.output)
	except Exception as why:
		logging.exception('Error while writing CSV file %s : %s', args.output, why)
		raise
