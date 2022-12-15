#!/usr/bin/env python3
import logging
import argparse
from pathlib import Path
from voprov.models.model import VOProvDocument, VOPROV
from voprov.visualization.dot import prov_to_dot
from utils import get_commit_version

SPOCA_PROGRAM_DIR = Path(__file__).parent.parent / 'SPoCA/programs/'

# IT is OK to add the same namespace several time to the provenance doc, it will not create duplicates

class Provenance:
	def __init__(self, prov_doc):
		self.prov_doc = prov_doc
	
	def add_activity(self, identifier, description):
		try:
			return self.prov_doc.get_record(identifier)[0]
		except IndexError:
			return self.prov_doc.activity(
				identifier = identifier,
				name = min(description.get_attribute('prov:name')),
				activityDescription = description
			)
	
	def add_entity(self, identifier, location, description):
		try:
			return self.prov_doc.get_record(identifier)[0]
		except IndexError:
			return self.prov_doc.entity(
				identifier = identifier,
				name = min(description.get_attribute('prov:name')),
				location = location,
				entityDescription = description
			)
	
	def add_config_file(self, identifier, location, description):
		try:
			return self.prov_doc.get_record(identifier)[0]
		except IndexError:
			return self.prov_doc.configFile(
				identifier = identifier,
				name = min(description.get_attribute('prov:name')),
				location = location,
				configFileDescription = description
			)

class GetCalibratedAiaProvenance(Provenance):
	'''Provenance for the calibration of AIA image from level 1 to level 2'''
	
	def __init__(self, prov_doc, wavelength):
		super().__init__(prov_doc)
		
		self.prov_doc.add_namespace('jsoc', 'https://jsoc.stanford.edu/AIA/AIA_lev1.html')
		self.prov_doc.add_namespace('aiapy', 'https://gitlab.com/LMSAL_HUB/aia_hub/aiapy')
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		
		self.aia_level1_description = self.prov_doc.entityDescription(
			identifier = 'jsoc:aia.lev1 WAVELNTH = %s' % wavelength,
			name = 'SDO/AIA level 1 %sÅ' % wavelength,
			description = 'SDO/AIA image level 1 provided by JSOC',
			docurl = 'http://jsoc.stanford.edu/AIA/AIA_lev1.html',
			type = 'image FITS file'
		)
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'aiapy:calibrate',
			name = 'aia calibration',
			version = '0.6.4',
			description = 'Update pointing, fix observer location, register, correct degradation and normalize_exposure of the image',
			docurl = 'https://aiapy.readthedocs.io/en/stable/preparing_data.html',
			type = 'Calibration'
		)
		
		self.aia_level2_description = self.prov_doc.entityDescription(
			identifier = 'rob:aia_science_level2/%04d' % wavelength,
			name = 'SDO/AIA level 2 %sÅ' % wavelength,
			description = 'SDO/AIA image calibrated using aiapy',
			docurl = 'http://sdo.oma.be/',
			type = 'image FITS file'
		)
		
		self.used_image_description = self.prov_doc.usageDescription(
			identifier = 'rob:aia_calibration used image',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.aia_level1_description
		)
		
		self.generated_image_description = self.prov_doc.generationDescription(
			identifier = 'rob:aia_calibration generated image',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.aia_level2_description
		)


class GetCalibratedHmiProvenance(Provenance):
	'''Provenance for the calibration of HMI magnetogram images from level 1 to level 1.5'''
	
	def __init__(self, prov_doc):
		super().__init__(prov_doc)
		
		self.prov_doc.add_namespace('jsoc', 'https://jsoc.stanford.edu/AIA/AIA_lev1.html')
		self.prov_doc.add_namespace('solarsoft', 'https://www.lmsal.com/solarsoft/')
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		
		self.hmi_level1_description = self.prov_doc.entityDescription(
			identifier = 'jsoc:hmi.m_45s',
			name = 'HMI magnetogram level 1',
			description = 'SDO/HMI line-of-sight magnetic field image level 1',
			docurl = 'http://jsoc.stanford.edu/jsocwiki/hmi.M-45s-info',
			type = 'image FITS file'
		)
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'solarsoft:aia_prep',
			name = 'aia_prep',
			version = 'V5.10',
			description = 'Register the image',
			docurl = 'https://sdo-analysis-guide.readthedocs.io/en/latest/process/aia_prep.html',
			type = 'Calibration'
		)
		
		self.hmi_level1_5_description = self.prov_doc.entityDescription(
			identifier = 'rob:hmi magnetogram level1.5',
			name = 'HMI magnetogram level 1.5',
			description = 'SDO/HMI line-of-sight magnetic field image registered using SOLARSOFT aia_prep',
			docurl = 'http://sdo.oma.be/',
			type = 'image FITS file'
		)
		
		self.used_image_description = self.prov_doc.usageDescription(
			identifier = 'rob:hmi_calibration used image',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.hmi_level1_description
		)
		
		self.generated_image_description = self.prov_doc.generationDescription(
			identifier = 'rob:hmi_calibration generated image',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.hmi_level1_5_description
		)


class GetClassCentersProvenance(Provenance):
	'''Provenance for the computation of class centers'''
	
	def __init__(self, prov_doc, image_descriptions):
		super().__init__(prov_doc)
		
		self.image_descriptions = image_descriptions
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		self.prov_doc.add_namespace('spoca', 'https://github.com/bmampaey/SPoCA')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'spoca:classification',
			name = 'classification',
			version = get_commit_version(SPOCA_PROGRAM_DIR / 'classification.cpp'),
			description = 'Use fuzzy classification to compute the class centers of the intensities of the pixels of an image',
			docurl = 'https://github.com/bmampaey/SPoCA',
			type = 'Analysis'
		)
		
		self.config_file_description = self.prov_doc.configFileDescription(
			identifier = 'spoca:classification.config',
			activityDescription = self.activity_description,
			name = 'classification.config',
			contentType = 'SPoCA config file',
			description = 'Configuration file for the SPoCA classification program specifying the image preprocessing parameters, the classifier to use and it\'s parameters'
		)
		
		self.class_centers_file_description = self.prov_doc.entityDescription(
			identifier = 'rob:class_centers_file',
			name = 'class centers file',
			description = 'A text file with the class centers as computed by the SPoCA classification program',
			type = 'text file'
		)
		
		self.used_image_descriptions = [
			self.prov_doc.usageDescription(
				identifier = 'rob:classification used image',
				activityDescription = self.activity_description,
				role = 'image',
				type = 'Main',
				multiplicity = 1,
				entityDescription = image_description
			) for image_description in self.image_descriptions
		]
		
		self.generated_class_centers_file_description = self.prov_doc.generationDescription(
			identifier = 'rob:classification generated class_centers_file',
			activityDescription = self.activity_description,
			role = 'meta parameter',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.class_centers_file_description
		)


class GetMedianClassCentersProvenance(Provenance):
	'''Provenance for the computation of the mediane of class centers'''
	
	def __init__(self, prov_doc, class_centers_file_description):
		super().__init__(prov_doc)
		
		self.class_centers_file_description = class_centers_file_description
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'rob:compute_median_class_centers',
			name = 'compute median class centers',
			description = 'Compute the median of each class centers through time',
			type = 'Reduction'
		)
		
		self.median_class_centers_file_description = self.prov_doc.entityDescription(
			identifier = 'rob:median_class_centers_file',
			name = 'median class centers file',
			description = 'A text file with the fix class centers for the SPoCA attribution program',
			type = 'text file'
		)
		
		self.used_class_centers_file_description = self.prov_doc.usageDescription(
			identifier = 'rob:compute_median_class_centers used class_centers_file',
			activityDescription = self.activity_description,
			role = 'meta parameter',
			type = 'Main',
			multiplicity = '1..*',
			entityDescription = self.class_centers_file_description
		)
		
		self.generated_median_class_centers_file_description = self.prov_doc.generationDescription(
			identifier = 'rob:compute_median_class_centers generated median_class_centers_file',
			activityDescription = self.activity_description,
			role = 'meta parameter',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.median_class_centers_file_description
		)


class GetSegmentationMapProvenance(Provenance):
	'''Provenance for the creation of segmentation map'''
	
	def __init__(self, prov_doc, class_centers_file_description, image_descriptions):
		super().__init__(prov_doc)
		
		self.class_centers_file_description = class_centers_file_description
		self.image_descriptions = image_descriptions
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		self.prov_doc.add_namespace('spoca', 'https://github.com/bmampaey/SPoCA')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'spoca:attribution',
			name = 'attribution',
			version = get_commit_version(SPOCA_PROGRAM_DIR / 'attribution.cpp'),
			description = 'Use fuzzy classification with fixed class centers to compute the probability of each pixel of an image to belong to each class, then select the class with the highest probability for each pixel',
			docurl = 'https://github.com/bmampaey/SPoCA',
			type = 'Selection'
		)
		
		self.config_file_description = self.prov_doc.configFileDescription(
			identifier = 'spoca:attribution.config',
			activityDescription = self.activity_description,
			name = 'attribution.config',
			contentType = 'SPoCA config file',
			description = 'Configuration file for the SPoCA attribution program specifying the image preprocessing parameters, the classifier to use and it\'s parameters'
		)
		
		self.segmentation_map_description = self.prov_doc.entityDescription(
			identifier = 'rob:segmentation_map',
			name = 'segmentation map',
			description = 'An image where each pixel has been attributed to a single class',
			type = 'image FITS file'
		)
		
		self.used_class_centers_file_description = self.prov_doc.usageDescription(
			identifier = 'rob:attribution used class_centers_file',
			activityDescription = self.activity_description,
			role = 'meta parameter',
			type = 'Setup',
			multiplicity = 1,
			entityDescription = self.class_centers_file_description
		)
		
		self.used_image_descriptions = [
			self.prov_doc.usageDescription(
				identifier = 'rob:attribution used image',
				activityDescription = self.activity_description,
				role = 'image',
				type = 'Main',
				multiplicity = 1,
				entityDescription = image_description
			) for image_description in self.image_descriptions
		]
		
		self.generated_segmentation_map_description = self.prov_doc.generationDescription(
			identifier = 'rob:attribution generated segmentation_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.segmentation_map_description
		)
	
	def add_provenance_from_activity_log(self, log):
		'''Add provenance from an activity log to the provenance document'''
		
		activity = self.add_activity('rob:%s' % log['activity_id'], self.activity_description)
		
		config_file = self.add_config_file('spoca4tap:%s' % Path(log['function_callargs']['config']['config_file']).name, log['function_callargs']['config']['config_file'], self.config_file_description)
		
		class_centers_file = self.add_entity('rob:%s' % Path(log['function_callargs']['config']['centers_file']).name, log['function_callargs']['config']['centers_file'], self.class_centers_file_description)
		
		images = [self.add_entity('rob:%s' % Path(image).name, image, image_description) for image, image_description in zip(log['function_callargs']['images'], self.image_descriptions)]
		
		segmentation_map = self.add_entity('rob:%s' % Path(log['function_output']).name, log['function_output'], self.segmentation_map_description)
		
		self.prov_doc.configuration(configured = activity, configurator = config_file, artefactType = 'ConfigFile')
		
		activity.used(class_centers_file, attributes = {'prov:role': 'meta parameter'})
		
		for image in images:
			activity.used(image, attributes = {'prov:role': 'image'})
		
		segmentation_map.wasGeneratedBy(activity)


class GetChMapProvenance(Provenance):
	'''Provenance for the creation of ch map'''
	
	def __init__(self, prov_doc, segmentation_map_description, stat_image_descriptions):
		super().__init__(prov_doc)
		
		self.segmentation_map_description = segmentation_map_description
		self.stat_image_descriptions = stat_image_descriptions
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		self.prov_doc.add_namespace('spoca', 'https://github.com/bmampaey/SPoCA')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'spoca:get_ch_map',
			name = 'get_CH_map',
			version = get_commit_version(SPOCA_PROGRAM_DIR / 'get_CH_map.cpp'),
			description = 'Use image transformation to group the individual pixels of an image into regions',
			docurl = 'https://github.com/bmampaey/SPoCA',
			type = 'Reduction'
		)
		
		self.config_file_description = self.prov_doc.configFileDescription(
			identifier = 'spoca:get_ch_map.config',
			activityDescription = self.activity_description,
			name = 'get_ch_map.config',
			contentType = 'SPoCA config file',
			description = 'Configuration file for the SPoCA get_CH_map program specifying the image transformations to apply and their parameters'
		)
		
		self.ch_map_description = self.prov_doc.entityDescription(
			identifier = 'rob:ch_map',
			name = 'coronal hole map',
			description = 'An image where each pixel has been attributed to a region or to no region',
			type = 'image FITS file'
		)
		
		self.used_segmentation_map_description = self.prov_doc.usageDescription(
			identifier = 'rob:get_ch_map used segmentation_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.segmentation_map_description
		)
		
		self.used_stat_image_descriptions = {
			name : self.prov_doc.usageDescription(
				identifier = 'rob:get_ch_map used %s' % name,
				activityDescription = self.activity_description,
				role = 'image',
				type = 'Main',
				multiplicity = 1,
				entityDescription = stat_image_description
			) for name, stat_image_description in self.stat_image_descriptions.items()
		}
		
		self.generated_ch_map_description = self.prov_doc.generationDescription(
			identifier = 'rob:get_ch_map generated ch_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.ch_map_description
		)
	
	def add_provenance_from_activity_log(self, log):
		'''Add provenance from an activity log to the provenance document'''
		
		activity = self.add_activity('rob:%s' % log['activity_id'], self.activity_description)
		
		config_file = self.add_config_file('spoca4tap:%s' % Path(log['function_callargs']['config']['config_file']).name, log['function_callargs']['config']['config_file'], self.config_file_description)
		
		segmentation_map = self.add_entity('rob:%s' % Path(log['function_callargs']['segmentation_map']).name, log['function_callargs']['segmentation_map'], self.segmentation_map_description)
		
		stat_images = {
			name : self.add_entity('rob:%s' % Path(image).name, image, self.stat_image_descriptions[name])
			for name, image in log['function_callargs']['stat_images'].items() if image is not None
		}
		
		ch_map = self.add_entity('rob:%s' % Path(log['function_output']).name, log['function_output'], self.ch_map_description)
		
		self.prov_doc.configuration(configured = activity, configurator = config_file, artefactType = 'ConfigFile')
		
		activity.used(segmentation_map, attributes = {'prov:role': 'image'})
		
		for stat_image in stat_images.values():
			activity.used(stat_image, attributes = {'prov:role': 'image'})
		
		ch_map.wasGeneratedBy(activity)


class GetTrackedMapProvenance(Provenance):
	'''Provenance for the tracking of region maps'''
	
	def __init__(self, prov_doc, untracked_map_description):
		super().__init__(prov_doc)
		
		self.untracked_map_description = untracked_map_description
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		self.prov_doc.add_namespace('spoca', 'https://github.com/bmampaey/SPoCA')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'spoca:tracking',
			name = 'tracking',
			version = get_commit_version(SPOCA_PROGRAM_DIR / 'tracking.cpp'),
			description = 'Track the regions in successive regions maps using solar de-rotation and overlap comparison',
			docurl = 'https://github.com/bmampaey/SPoCA',
			type = 'Reduction'
		)
		
		self.config_file_description = self.prov_doc.configFileDescription(
			identifier = 'spoca:tracking.config',
			activityDescription = self.activity_description,
			name = 'tracking.config',
			contentType = 'SPoCA config file',
			description = 'Configuration file for the SPoCA tracking program'
		)
		
		self.tracked_map_description = self.prov_doc.entityDescription(
			identifier = 'rob:tracked_map',
			name = 'tracked map',
			description = 'An image where each pixel has been attributed to a region or to no region',
			type = 'image FITS file'
		)
		
		self.used_tracked_map_description = self.prov_doc.usageDescription(
			identifier = 'rob:tracking used tracked_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = '*',
			entityDescription = self.tracked_map_description
		)
		
		self.used_untracked_map_description = self.prov_doc.usageDescription(
			identifier = 'rob:tracking used untracked_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = '1..*',
			entityDescription = self.untracked_map_description
		)
		
		self.generated_tracked_map_description = self.prov_doc.generationDescription(
			identifier = 'rob:tracking generated tracked_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = '1..*',
			entityDescription = self.tracked_map_description
		)
	
	def add_provenance_from_activity_log(self, log):
		'''Add provenance from an activity log to the provenance document'''
		
		activity = self.add_activity('rob:%s' % log['activity_id'], self.activity_description)
		
		config_file = self.add_config_file('spoca4tap:%s' % Path(log['function_callargs']['config']['config_file']).name, log['function_callargs']['config']['config_file'], self.config_file_description)
		
		tracked_maps = [self.add_entity('rob:%s[tracked]' % Path(map).name, map, self.tracked_map_description) for map in log['function_callargs']['tracked_maps']]
		
		untracked_maps = [self.add_entity('rob:%s' % Path(map).name, map, self.untracked_map_description) for map in log['function_callargs']['untracked_maps']]
		
		new_tracked_maps = [self.add_entity('rob:%s[tracked]' % Path(map).name, map, self.tracked_map_description) for map in log['function_callargs']['untracked_maps']]
		
		self.prov_doc.configuration(configured = activity, configurator = config_file, artefactType = 'ConfigFile')
		
		for tracked_map in tracked_maps:
			activity.used(tracked_map, attributes = {'prov:role': 'image'})
		
		for untracked_map in untracked_maps:
			activity.used(untracked_map, attributes = {'prov:role': 'image'})
		
		for tracked_map in new_tracked_maps:
			tracked_map.wasGeneratedBy(activity)


class GetLonglivedRegionsColorsProvenance(Provenance):
	'''Provenance for the extraction of the colors of regions to keep from tracked region maps'''
	
	def __init__(self, prov_doc, tracked_map_description):
		super().__init__(prov_doc)
		
		self.tracked_map_description = tracked_map_description
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		self.prov_doc.add_namespace('spoca4tap', 'https://github.com/bmampaey/spoca4tap')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'spoca4tap:get_longlived_regions_colors',
			name = 'get_longlived_regions_colors',
			version = get_commit_version(Path(__file__).parent / 'get_longlived_regions_colors.py'),
			description = 'Analyze tracking information to compute the lifetime of regions in tracked region maps',
			type = 'Analysis'
		)
		
		self.get_longlived_regions_colors_parameter_min_lifetime_description = self.prov_doc.parameterDescription(
			identifier = 'rob:region_min_lifetime',
			activityDescription = self.activity_description,
			name = 'region minimum lifetime',
			valueType = 'time',
			description = 'The minimum lifetime of a region for it to be selected',
			ucd = 'time.duration'
		)
		
		self.longlived_regions_colors_description = self.prov_doc.entityDescription(
			identifier = 'rob:longlived_regions_colors',
			name = 'longlived regions colors',
			description = 'A list of the colors of regions that have a minimum lifetime',
			type = 'list of integers'
		)
		
		self.used_tracked_map_description = self.prov_doc.usageDescription(
			identifier = 'rob:get_longlived_regions_colors used tracked_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = '1..*',
			entityDescription = self.tracked_map_description
		)
		
		self.generated_longlived_regions_colors_description = self.prov_doc.generationDescription(
			identifier = 'rob:get_longlived_regions_colors generated longlived_regions_colors',
			activityDescription = self.activity_description,
			role = 'list',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.longlived_regions_colors_description
		)


class GetCleanedMapProvenance(Provenance):
	'''Provenance for the creation of cleaned region map'''
	
	def __init__(self, prov_doc, map_description, longlived_regions_colors_description):
		super().__init__(prov_doc)
		
		self.map_description = map_description
		self.longlived_regions_colors_description = longlived_regions_colors_description
		
		self.prov_doc.add_namespace('rob', 'https://www.astro.oma.be/')
		self.prov_doc.add_namespace('spoca4tap', 'https://github.com/bmampaey/spoca4tap')
		
		self.activity_description = self.prov_doc.activityDescription(
			identifier = 'spoca4tap:get_cleaned_map',
			name = 'get_cleaned_map',
			version = get_commit_version(Path(__file__).parent / 'get_cleaned_map.py'),
			description = 'Remove the shortlived regions from the region map',
			type = 'Selection'
		)
		
		self.cleaned_map_description = self.prov_doc.entityDescription(
			identifier = 'rob:cleaned_map',
			name = 'cleaned_map',
			description = 'An image where each pixel has been attributed to a region or to no region',
			type = 'image FITS file'
		)
		
		self.used_map_description = self.prov_doc.usageDescription(
			identifier = 'rob:get_cleaned_map used map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.map_description
		)
		
		self.used_longlived_regions_colors_description = self.prov_doc.usageDescription(
			identifier = 'rob:get_cleaned_map used longlived_regions_colors',
			activityDescription = self.activity_description,
			role = 'parameter',
			type = 'Setup',
			multiplicity = 1,
			entityDescription = self.longlived_regions_colors_description
		)
		
		self.generated_cleaned_map_description = self.prov_doc.generationDescription(
			identifier = 'rob:get_cleaned_map generated cleaned_map',
			activityDescription = self.activity_description,
			role = 'image',
			type = 'Main',
			multiplicity = 1,
			entityDescription = self.cleaned_map_description
		)
	
	def add_provenance_from_activity_log(self, log):
		'''Add provenance from an activity log to the provenance document'''
		
		activity = self.add_activity('rob:%s' % log['activity_id'], self.activity_description)
		
		longlived_regions_colors = self.add_entity('rob:longlived_regions_colors[%s-%s]' % (log['function_callargs']['longlived_regions_colors'][0], log['function_callargs']['longlived_regions_colors'][-1]), None, self.longlived_regions_colors_description)
		
		map = self.add_entity('rob:%s[tracked]' % Path(log['function_callargs']['region_map']).name, log['function_callargs']['region_map'], self.map_description)
		
		cleaned_map = self.add_entity('rob:%s[cleaned]' % Path(log['function_output']).name, log['function_output'], self.cleaned_map_description)
		
		activity.used(longlived_regions_colors, attributes = {'prov:role': 'parameter'})
		activity.used(map, attributes = {'prov:role': 'image'})
		
		cleaned_map.wasGeneratedBy(activity)


# Start point of the script
if __name__ == '__main__':
		
	# Get the arguments
	parser = argparse.ArgumentParser(description = 'Writes a provenance document with the description of the rob_spoca_ch TAP service')
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help = 'Set the logging level (default is INFO)')
	parser.add_argument('--output', '-o', default = 'provenance.json', help = 'Path to the output file (default is provenance.json)')
	parser.add_argument('--preview', '-p', default = 'provenance.png',help = 'Path to the preview image file (default is provenance.png)')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	prov_doc = VOProvDocument()
	
	# The default namespace must always be set
	prov_doc.set_default_namespace(VOPROV.uri)
	
	get_calibrated_aia = GetCalibratedAiaProvenance(prov_doc, 193)
	get_calibrated_hmi = GetCalibratedHmiProvenance(prov_doc)
	get_class_centers = GetClassCentersProvenance(prov_doc, [get_calibrated_aia.aia_level2_description])
	get_median_class_centers = GetMedianClassCentersProvenance(prov_doc, get_class_centers.class_centers_file_description)
	get_segmentation_map = GetSegmentationMapProvenance(prov_doc, get_median_class_centers.median_class_centers_file_description, [get_calibrated_aia.aia_level2_description])
	get_ch_map = GetChMapProvenance(prov_doc, get_segmentation_map.segmentation_map_description, {'aia_image': get_calibrated_aia.aia_level2_description, 'hmi_image': get_calibrated_hmi.hmi_level1_5_description})
	get_tracked_map = GetTrackedMapProvenance(prov_doc, get_ch_map.ch_map_description)
	get_longlived_regions_colors = GetLonglivedRegionsColorsProvenance(prov_doc, get_tracked_map.tracked_map_description)
	get_cleaned_map = GetCleanedMapProvenance(prov_doc, get_tracked_map.tracked_map_description, get_longlived_regions_colors.longlived_regions_colors_description)
	
	try:
		prov_doc.serialize(args.output, format = 'json')
	except Exception as why:
		logging.exception('Could not write provenance document %s: %s', args.output, why)
	else:
		logging.info('Wrote provenance file %s', args.output)
	
	try:
		dot = prov_to_dot(prov_doc, use_labels = True, direction = 'LR')
		dot.write_png(args.preview)
	except Exception as why:
		logging.exception('Could not write provenance preview image %s: %s', args.preview, why)
	else:
		logging.info('Wrote provenance preview image %s', args.preview)
