#!/usr/bin/env python3
import logging
import argparse

from utils import get_config, get_url, write_tap_parameters_to_csv

__all__ = ['get_tracking_tap_parameters_from_file']


def get_datalink_tap_parameters(granule_uids, overlay_image, aia_image, hmi_image, provenance, config):
	'''Extract the TAP parameters for the datalink table'''
	tap_parameters = list()
	
	thumbnail_url = get_url(overlay_image, config.get('map_overlay_base_url'), config.get('map_overlay_base_dir', None))
	ch_stat_aia_image_url = get_url(aia_image, config.get('aia_image_base_url'), config.get('aia_image_base_dir', None))
	ch_stat_hmi_image_url = get_url(hmi_image, config.get('hmi_image_base_url'), config.get('hmi_image_base_dir', None))
	provenance_url = get_url(provenance, config.get('provenance_base_url'), config.get('provenance_base_dir', None))

	
	for granule_uid in granule_uids:
		tap_parameters.append({
			'granule_uid': granule_uid,
			'thumbnail_url': thumbnail_url,
			'ch_stat_aia_image_url': ch_stat_aia_image_url,
			'ch_stat_hmi_image_url': ch_stat_hmi_image_url,
			'provenance_url': provenance_url
		})
	
	return tap_parameters

# Start point of the script

if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description = get_datalink_tap_parameters.__doc__)
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--config-file', '-c', required = True, help = 'Path to the config file of the script')
	parser.add_argument('--output', '-o', default = 'rob_spoca_ch.datalink.csv', help = 'The file path for the output CSV file (default is rob_spoca_ch.datalink.csv)')
	parser.add_argument('--granule-uid', '-g', action = 'append', required = True, metavar = 'GRANULE UID', help = 'A granule uid corresponding to the following maps and image')
	parser.add_argument('overlay_image', metavar = 'FILEPATH', help = 'The file path to the overlay image of the cleaned SPoCA CH map')
	parser.add_argument('aia_image', metavar = 'FILEPATH', help = 'The file path to AIA image used to compute the statistics')
	parser.add_argument('hmi_image', metavar = 'FILEPATH', help = 'The file path to HMI image used to compute the statistics')
	parser.add_argument('provenance', nargs='?', metavar = 'FILEPATH', help = 'The file path to the provenance of the cleaned SPoCA CH map')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	# Parse the script config file
	config = get_config(args.config_file)
	
	try:
		tap_parameters = get_datalink_tap_parameters(args.granule_uid, args.overlay_image, args.aia_image, args.hmi_image, args.provenance, config['TAP_PARAMETERS'])
	except Exception as why:
		logging.exception('Could not extract TAP parameters for granule uids %s: %s', args.granule_uid, why)
		raise
	
	try:
		write_tap_parameters_to_csv(tap_parameters, args.output)
	except Exception as why:
		logging.exception('Error while writing CSV file %s : %s', args.output, why)
		raise
