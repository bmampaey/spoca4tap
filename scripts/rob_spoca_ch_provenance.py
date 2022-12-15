#!/usr/bin/env python3
import logging
import argparse
import json
from pathlib import Path
from voprov.models.model import VOProvDocument, VOPROV
from voprov.visualization.dot import prov_to_dot

from provenance import GetCalibratedAiaProvenance, GetCalibratedHmiProvenance, GetClassCentersProvenance, GetMedianClassCentersProvenance, GetSegmentationMapProvenance, GetChMapProvenance, GetTrackedMapProvenance, GetLonglivedRegionsColorsProvenance, GetCleanedMapProvenance

# Start point of the script
if __name__ == '__main__':
	
	# Get the arguments
	parser = argparse.ArgumentParser(description='Writes a provenance document from an activity log file for the rob_spoca_ch TAP service')
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--output', '-o', default = 'provenance.json', help = 'Path to the output file (default is provenance.json)')
	parser.add_argument('--preview', '-p', help = 'Path to the preview image file')
	parser.add_argument('activity_logs', metavar = 'FILEPATH', nargs = '+', help = 'The path to an activity log file')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	prov_doc = VOProvDocument()
	
	# The default namespace must always be set
	prov_doc.set_default_namespace(VOPROV.uri)
	
	# Set up the description of all activities
	get_calibrated_aia = GetCalibratedAiaProvenance(prov_doc, 193)
	get_calibrated_hmi = GetCalibratedHmiProvenance(prov_doc)
	get_class_centers = GetClassCentersProvenance(prov_doc, [get_calibrated_aia.aia_level2_description])
	get_median_class_centers = GetMedianClassCentersProvenance(prov_doc, get_class_centers.class_centers_file_description)
	get_segmentation_map = GetSegmentationMapProvenance(prov_doc, get_median_class_centers.median_class_centers_file_description, [get_calibrated_aia.aia_level2_description])
	get_ch_map = GetChMapProvenance(prov_doc, get_segmentation_map.segmentation_map_description, {'aia_image': get_calibrated_aia.aia_level2_description, 'hmi_image': get_calibrated_hmi.hmi_level1_5_description})
	get_tracked_map = GetTrackedMapProvenance(prov_doc, get_ch_map.ch_map_description)
	get_longlived_regions_colors = GetLonglivedRegionsColorsProvenance(prov_doc, get_tracked_map.tracked_map_description)
	get_cleaned_map = GetCleanedMapProvenance(prov_doc, get_tracked_map.tracked_map_description, get_longlived_regions_colors.longlived_regions_colors_description)
	
	for activity_log in args.activity_logs:
		with open(activity_log, 'rt') as file:
			log = json.load(file)
		
		function_name = log['function_name']
		
		if function_name == 'get_segmentation_map':
			get_segmentation_map.add_provenance_from_activity_log(log)
		elif function_name == 'get_region_map':
			get_ch_map.add_provenance_from_activity_log(log)
		elif function_name == 'get_tracked_map':
			get_tracked_map.add_provenance_from_activity_log(log)
		elif function_name == 'get_cleaned_map':
			get_cleaned_map.add_provenance_from_activity_log(log)
		else:
			raise ValueError('Unknown function %s, cannot generate provenance doc' % function_name)
	
	try:
		prov_doc.serialize(args.output, format= 'json')
	except Exception as why:
		logging.exception('Could not write provenance document %s: %s', args.output, why)
	else:
		logging.info('Wrote provenance file %s', args.output)
	
	if args.preview:
		try:
			dot = prov_to_dot(prov_doc, use_labels= True, direction= 'LR')
			dot.write_png(args.preview)
		except Exception as why:
			logging.exception('Could not write provenance preview image %s: %s', args.preview, why)
		else:
			logging.info('Wrote provenance preview image %s', args.preview)
