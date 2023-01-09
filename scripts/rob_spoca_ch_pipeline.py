#!/usr/bin/env python3
import logging
import argparse
import multiprocessing
from datetime import datetime, timedelta
from pathlib import Path

from sdo_data import SdoData
from get_segmentation_map import get_segmentation_map
from get_region_map import get_region_map
from get_tracked_map import get_tracked_map
from get_longlived_regions_colors import get_longlived_regions_colors, write_regions_colors
from get_cleaned_map import get_cleaned_map
from get_overlay_image import get_overlay_image
from get_epn_core_tap_parameters import get_epn_core_tap_parameters_from_file
from get_tracking_tap_parameters import get_tracking_tap_parameters_from_file
from get_datalink_tap_parameters import get_datalink_tap_parameters
from utils import date_range, get_config, date_to_filename, date_from_filename, write_tap_parameters_to_csv, save_activity_log


def create_segmentation_maps(aia_images, config):
	'''Create the segmentation maps in parralel'''
	
	segmentation_maps = dict()
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		
		for date, images in aia_images.items():
			if None in images:
				logging.info('Image missing for date %s, cannot create segmentation map', date.isoformat())
				continue
			
			try:
				jobs[date] = pool.apply_async(get_segmentation_map, (date, images, config))
			except Exception as why:
				logging.exception('Could not start job get_segmentation_map : %s', why)
		
		for date, job in jobs.items():
			try:
				segmentation_maps[date] = job.get()
			except Exception as why:
				logging.exception('Could not create segmentation map for date %s: %s', date.isoformat(), why)
	
	return segmentation_maps


def create_ch_maps(segmentation_maps, stat_images, config):
	'''Create the ch maps in parralel'''
	
	ch_maps = dict()
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		
		for date, segmentation_map in segmentation_maps.items():
			try:
				jobs[(date, segmentation_map)] = pool.apply_async(get_region_map, (date, segmentation_map, stat_images[date], config))
			except Exception as why:
				logging.exception('Could not start job get_region_map : %s', why)
		
		for (date, segmentation_map), job in jobs.items():
			try:
				ch_maps[date] = job.get()
			except Exception as why:
				logging.exception('Could not create ch map for segmentation map %s: %s', segmentation_map, why)
	
	return ch_maps


def run_tracking(tracked_maps, untracked_maps, config):
	'''Run the tracking sequentially'''
	
	# Run the tracking on smaller groups of maps because all maps will be loaded in RAM at the same time
	# This requires the maps to be sorted chronologically
	tracked_maps = sorted((date_from_filename(map), map) for map in tracked_maps)
	untracked_maps = sorted(untracked_maps.items())
	overlap_count = config.getint('overlap_count')
	group_count =  config.getint('group_count')
	
	for untracked_map_group in (untracked_maps[i:i+group_count] for i in range(0, len(untracked_maps), group_count)):
		try:
			get_tracked_map([t[1] for t in tracked_maps[-overlap_count:]], [t[1] for t in untracked_map_group], config)
		except Exception as why:
			logging.exception('Could not execute get_tracked_map on maps %s: %s', untracked_map_group, why)
			raise
		
		tracked_maps += untracked_map_group
	
	return dict(tracked_maps)


def create_cleaned_maps(maps, longlived_regions_colors, end_date, config):
	'''Create the cleaned maps in parralel'''
	
	cleaned_maps = dict()
	uncleaned_ch_maps = dict()
	
	# Don't process the last maps because we don't know the real lifespan of the regions yet
	max_date = end_date - config.gettimedelta('min_lifespan')
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		
		for date, map in maps.items():
			if date < max_date:
				jobs[(date, map)] = pool.apply_async(get_cleaned_map, (date, map, longlived_regions_colors, config))
			else:
				logging.warning('Not writting cleaned map for map %s: the date is too close to the end "%s" to know the definitive lifespan', map, end_date.isoformat())
				uncleaned_ch_maps[date] = map
		
		for (date, map), job in jobs.items():
			try:
				cleaned_maps[date] = job.get()
			except Exception as why:
				logging.exception('Could not write cleaned map for map %s: %s', map, why)
	
	return cleaned_maps, uncleaned_ch_maps


def create_overlay_images(maps, background_images, config):
	'''Create the overlay images in parralel'''
	
	overlay_images = dict()
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		
		for date, map in maps.items():
			try:
				jobs[(date, map)] = pool.apply_async(get_overlay_image, (date, map, background_images[date], config))
			except Exception as why:
				logging.exception('Could not start job get_overlay_image : %s', why)
		
		for (date, map), job in jobs.items():
			try:
				overlay_images[date] = job.get()
			except Exception as why:
				logging.exception('Could not create overlay for map %s: %s', map, why)
	
	return overlay_images


def extract_epn_core_tap_parameters(cleaned_ch_maps, tracked_ch_maps, overlay_images, longlived_regions_colors, config):
	'''Extract the epn_core TAP parameters'''
	
	tap_parameters = dict()
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		# While creating cleaned maps from tracked maps, the last few ones are not created because we are not sure of the lifetime yet
		# As a result there are less cleaned maps than tracked maps, and we must only submit TAP parameters for wich there is a cleaned map
		for date, cleaned_ch_map in cleaned_ch_maps.items():
			try:
				tracked_ch_map = tracked_ch_maps[date]
			except KeyError:
				logging.info('No tracked map found for map %s', cleaned_ch_map)
			else:
				try:
					jobs[(date, tracked_ch_map)] = pool.apply_async(get_epn_core_tap_parameters_from_file, (tracked_ch_map, cleaned_ch_map, overlay_images.get(date), longlived_regions_colors, config))
				except Exception as why:
					logging.exception('Could not start job get_epn_core_tap_parameters_from_file : %s', why)
				
		
		for (date, tracked_ch_map), job in jobs.items():
			try:
				tap_parameters[date] = job.get()
			except Exception as why:
				logging.exception('Could not get epn_core TAP parameters for map %s : %s', tracked_ch_map, why)
	
	return tap_parameters


def extract_tracking_tap_parameters(cleaned_ch_maps, tracked_ch_maps, longlived_regions_colors, config):
	'''Extract the tracking TAP parameters'''
	
	tap_parameters = dict()
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		
		# While creating cleaned maps from tracked maps, the last few ones are not created because we are not sure of the lifetime yet
		# As a result there are less cleaned maps than tracked maps, and we must only submit TAP parameters for wich there is a cleaned map
		for date, cleaned_ch_map in cleaned_ch_maps.items():
			try:
				tracked_ch_map = tracked_ch_maps[date]
			except KeyError:
				logging.info('No tracked map found for map %s', cleaned_ch_map)
			else:
				try:
					jobs[(date, tracked_ch_map)] = pool.apply_async(get_tracking_tap_parameters_from_file, (tracked_ch_map, longlived_regions_colors))
				except Exception as why:
					logging.exception('Could not start job get_tracking_tap_parameters_from_file : %s', why)
		
		for (date, tracked_ch_map), job in jobs.items():
			try:
				tap_parameters[date] = job.get()
			except Exception as why:
				logging.exception('Could not get tracking TAP parameters for map %s : %s', tracked_ch_map, why)
	
	return tap_parameters


def extract_datalink_tap_parameters(epn_core_tap_parameters, overlay_images, stat_images, config):
	'''Extract the datalink TAP parameters'''
	
	tap_parameters = dict()
	
	with multiprocessing.Pool() as pool:
		jobs = dict()
		
		for date, epn_core_tap_parameter_list in epn_core_tap_parameters.items():
			granule_uids = [epn_core_tap_parameter['granule_uid'] for epn_core_tap_parameter in epn_core_tap_parameter_list]
			overlay_image = overlay_images.get(date)
			aia_image = stat_images.get(date, {}).get('aia_image')
			hmi_image = stat_images.get(date, {}).get('hmi_image')
			# TODO use the actual provenance file
			provenance = '{date}.provenance.json'.format(date = date_to_filename(date))
			
			try:
				jobs[date] = pool.apply_async(get_datalink_tap_parameters, (granule_uids, overlay_image, aia_image, hmi_image, provenance, config))
			except Exception as why:
				logging.exception('Could not start job get_datalink_tap_parameters : %s', why)
				
		
		for date, job in jobs.items():
			try:
				tap_parameters[date] = job.get()
			except Exception as why:
				logging.exception('Could not get datalink TAP parameters for date %s : %s', date, why)
	
	return tap_parameters


def write_tap_parameters(tap_parameters, output_file_pattern):
	'''Write all the TAP parameters to file'''
	
	for date, parameters in tap_parameters.items():
		output_file = output_file_pattern.format(date = date_to_filename(date))
		
		try:
			write_tap_parameters_to_csv(parameters, output_file)
		except Exception as why:
			logging.exception('Error while writing CSV file %s : %s', output_file, why)
		else:
			logging.info('wrote TAP parameters CSV file %s', output_file)


# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description='Pipeline to create CH maps and extract TAP parameters from AIA science level 2 images for the rob_spoca_ch TAP service')
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--start-date', '-s', required = True, type = datetime.fromisoformat, help = 'Start date of AIA files (ISO 8601 format)')
	parser.add_argument('--end-date', '-e', default = datetime.utcnow(), type = datetime.fromisoformat, help = 'End date of AIA files (ISO 8601 format)')
	parser.add_argument('--interval', '-i', default = 6, type = int, help = 'Number of hours between two results')
	parser.add_argument('--tracked-ch-maps', '-m', metavar = 'FILEPATH', nargs = '*', default = [], type = Path, help = 'The path to a previously tracked ch map to establish tracking relations with the past')
	parser.add_argument('--regions-colors', '-r', metavar = 'FILEPATH', default = 'longlived_regions_colors.txt', help = 'The path to a file with the list of regions color numbers for which to extract TAP parameters (default is longlived_regions_colors.txt)')
	
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	save_activity_log.output_directory = config.get('LOGGING', 'output_directory')
	
	# Setup the SDO data file lookup
	aia_data = SdoData(
		file_pattern = config.get('AIA_DATA', 'file_pattern'),
		hdu_name_or_index = config.getint('AIA_DATA', 'hdu_index'),
		ignore_quality_bits = config.getintlist('AIA_DATA', 'ignore_quality_bits'),
	)
	
	hmi_data = SdoData(
		file_pattern = config.get('HMI_DATA', 'file_pattern'),
		hdu_name_or_index = config.getint('HMI_DATA', 'hdu_index'),
		ignore_quality_bits = config.getintlist('HMI_DATA', 'ignore_quality_bits'),
	)
	
	aia_images = dict()
	for date in date_range(args.start_date, args.end_date, timedelta(hours=args.interval)):
		aia_images[date] = [aia_data.get_good_quality_file(date = date, wavelength = wavelength) for wavelength in config.getintlist('GET_SEGMENTATION_MAP', 'aia_wavelengths')]
	
	segmentation_maps = create_segmentation_maps(aia_images, config['GET_SEGMENTATION_MAP'])
	
	stat_images = dict()
	for date in segmentation_maps.keys():
		stat_images[date] = {
			'aia_image': aia_data.get_good_quality_file(date = date, wavelength = config.getint('GET_REGION_MAP', 'aia_wavelength')),
			'hmi_image': hmi_data.get_good_quality_file(date = date)
		}
	
	ch_maps = create_ch_maps(segmentation_maps, stat_images, config['GET_REGION_MAP'])
	
	tracked_ch_maps = run_tracking(args.tracked_ch_maps, ch_maps, config['GET_TRACKED_MAP'])
	
	# Extract the colors of regions to keep
	try:
		longlived_regions_colors = get_longlived_regions_colors(sorted(tracked_ch_maps.values()), config['LIFESPAN_CLEANING'])
	except Exception as why:
		logging.exception('Error getting longlived regions colors from maps : %s', why)
		raise
	
	try:
		write_regions_colors(longlived_regions_colors, args.regions_colors)
	except Exception as why:
		logging.exception('Error while writing text file %s : %s', args.regions_colors, why)
	else:
		logging.info('Wrote longlived regions colors to file %s', args.regions_colors)
	
	cleaned_ch_maps, uncleaned_ch_maps = create_cleaned_maps(tracked_ch_maps, longlived_regions_colors, args.end_date, config['LIFESPAN_CLEANING'])
	
	background_images = dict()
	for date in cleaned_ch_maps.keys():
		background_images[date] = aia_data.get_good_quality_file(date = date, wavelength = config.getint('GET_OVERLAY_IMAGE', 'aia_wavelength'))
	
	overlay_images = create_overlay_images(cleaned_ch_maps, background_images, config['GET_OVERLAY_IMAGE'])
	
	epn_core_tap_parameters = extract_epn_core_tap_parameters(cleaned_ch_maps, tracked_ch_maps, overlay_images, longlived_regions_colors, config['TAP_PARAMETERS'])
	write_tap_parameters(epn_core_tap_parameters, config.get('TAP_PARAMETERS', 'epn_core_output_file'))
	
	tracking_tap_parameters = extract_tracking_tap_parameters(cleaned_ch_maps, tracked_ch_maps, longlived_regions_colors, config['TAP_PARAMETERS'])
	write_tap_parameters(tracking_tap_parameters, config.get('TAP_PARAMETERS', 'tracking_output_file'))
	
	datalink_tap_parameters = extract_datalink_tap_parameters(epn_core_tap_parameters, overlay_images, stat_images, config['TAP_PARAMETERS'])
	write_tap_parameters(datalink_tap_parameters, config.get('TAP_PARAMETERS', 'datalink_output_file'))
	
	logging.info('At next execution of the script, pass the parameter --tracked-ch-maps %s', ' '.join(str(map) for map in uncleaned_ch_maps.values()))
