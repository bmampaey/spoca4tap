#!/usr/bin/env python3
import logging
import argparse
from datetime import datetime
from glob import glob
from functools import lru_cache
from astropy.io import fits

__all__ = ['SdoData']

class SdoData:
	'''Helper to find good quality SDO data'''
	
	# Definition of the bits in the FITS header QUALITY keyword
	QUALITY_BITS = {
		0	: 'FLAT_REC == MISSING (Flatfield data not available)',
		1	: 'ORB_REC == MISSING (Orbit data not available)',
		2	: 'ASD_REC == MISSING (Ancillary Science Data not available)',
		3	: 'MPO_REC == MISSING (Master pointing data not available)',
		4	: 'RSUN_LF == MISSING or X0_LF == MISSING or Y0_LF == MISSING (HMI Limb fit not acceptable)',
		5	: '',
		6	: '',
		7	: '',
		8	: 'MISSVALS > 0',
		9	: 'MISSVALS > 0.01*TOTVALS',
		10	: 'MISSVALS > 0.05*TOTVALS',
		11	: 'MISSVALS > 0.25*TOTVALS',
		12	: 'ACS_MODE != "SCIENCE" (Spacecraft not in science pointing mode)',
		13	: 'ACS_ECLP == "YES" (Spacecraft eclipse flag set)',
		14	: 'ACS_SUNP == "NO" (Spacecraft sun presence flag not set)',
		15	: 'ACS_SAFE == "YES" (Spacecraft safemode flag set)',
		16	: 'IMG_TYPE == "DARK" (Dark image)',
		17	: 'HWLTNSET == "OPEN" or AISTATE == "OPEN" (HMI ISS loop open or  AIA ISS loop Open)',
		18	: '(FID >= 1 and FID <= 9999) or (AIFTSID >= 0xC000)  (HMI Calibration Image or AIA Calibration Image)',
		19	: 'HCFTID == 17 (HMI CAL mode image)',
		20	: '(AIFCPS <= -20 or AIFCPS >= 100) (AIA focus out of range)',
		21	: 'AIAGP6 != 0 (AIA register flag)',
		22	: '',
		23	: '',
		24	: '',
		25	: '',
		26	: '',
		27	: '',
		28	: '',
		29	: '',
		30	: 'Quicklook image',
		31	: 'Image not available'
	}
	
	# Default name for the QUALITY keyword (SDO FITS files have also a QUALITY0 keyword)
	QUALITY_KEYWORD = 'QUALITY'
	
	# Default quality bits that can be ignored
	IGNORE_QUALITY_BITS = [0, 1, 2, 3, 4, 8]
	
	# Default HDU index of the FITS file that contains the QUALITY keyword
	# Typically SDO data is tiled compressed, so the keywords are in the second HDU
	HDU_INDEX = 1
	
	# File pattern for AIA FITS files that can be formated with a date and a wavelength
	# File pattern for HMI FITS files that can be formated with a date
	def __init__(self, file_pattern, hdu_name_or_index = None, quality_keyword = None, ignore_quality_bits = None):
		self.file_pattern = file_pattern
		self.hdu_name_or_index = hdu_name_or_index if hdu_name_or_index is not None else self.HDU_INDEX
		self.quality_keyword = quality_keyword if quality_keyword is not None else self.QUALITY_KEYWORD
		self.ignore_quality_bits = ignore_quality_bits if ignore_quality_bits is not None else self.IGNORE_QUALITY_BITS
	
	def get_files(self, **pattern_values):
		'''Return the paths of the files that matches the file pattern and specified pattern values'''
		file_glob = self.file_pattern.format(**pattern_values)
		logging.debug('File glob for pattern values %s is %s', pattern_values, file_glob)
		return sorted(glob(file_glob))
	
	@lru_cache
	def get_good_quality_file(self, **pattern_values):
		'''Return the paths of the first file that matches the file pattern and specified pattern values, and has a good quality'''
		
		for file_path in self.get_files(**pattern_values):
			
			# Get the quality of the file
			try:
				quality = self.get_quality(file_path)
			except Exception as why:
				logging.warning('Could not get quality for file %s: %s', file_path, why)
				continue
			else:
				logging.debug('Quality of file %s: %s', file_path, self.get_quality_errors(quality))
			
			# Set the ignored quality bits to 0
			for bit in self.ignore_quality_bits:
				quality &= ~(1<<bit)
			
			# A quality of 0 means no defect
			if quality == 0:
				return file_path
			else:
				logging.debug('Skipping file %s with bad quality: %s', file_path, self.get_quality_errors(quality))
	
	def get_quality(self, file_path):
		'''Return the value of the quality keyword in the header of a FITS file'''
		with fits.open(file_path) as hdulist:
			return hdulist[self.hdu_name_or_index].header[self.quality_keyword]
	
	@classmethod
	def get_quality_errors(cls, quality):
		'''Return the set of errors corresponding to the bits set in the quality value'''
		errors = set()
		for bit, msg in cls.QUALITY_BITS.items():
			if quality & (1 << bit):
				errors.add(msg or 'Unknown error')
		return errors

# Start point of the script
if __name__ == '__main__':
	
	# Default value for the aia-file-pattern argument valid for the spoca.oma.be server
	AIA_FILE_PATTERN = '/data/sdo/aia_science_level2/{wavelength:04d}/{date:%Y/%m/%d}/aia_science_level2.{wavelength:04d}.{date:%Y%m%d_%H}*.fits'
	
	parser = argparse.ArgumentParser(description='Prints AIA FITS filepaths for the specified date and wavelength')
	parser.add_argument('--verbose', '-v', choices = ['DEBUG', 'INFO', 'ERROR'], default = 'INFO', help='Set the logging level (default is INFO)')
	parser.add_argument('--aia-file-pattern', '-A', metavar = 'FILE PATTERN', default = AIA_FILE_PATTERN, help='A file pattern for AIA FITS files that can be formated with a date and a wavelength')
	parser.add_argument('--hdu-index', '-H', type = int, help='The HDU index of the header that contains the quality keyword')
	parser.add_argument('--quality-keyword', '-K', metavar = 'KEYWORD', help='The name of the quality keyword')
	parser.add_argument('--ignore-quality-bits', '-I', metavar = 'QUALITY BIT NUMBER', type = int, action='append', help='The quality bits that can be ignored')
	parser.add_argument('date', type = datetime.fromisoformat, help = 'A date in ISO format')
	parser.add_argument('wavelength', type = int, help = 'An AIA wavelength in Ångström')
	
	args = parser.parse_args()
	
	# Setup the logging
	logging.basicConfig(level = getattr(logging, args.verbose), format = '%(asctime)s %(levelname)-8s: %(message)s')
	
	aia_data = SdoData(file_pattern = args.aia_file_pattern, hdu_name_or_index = args.hdu_index, quality_keyword = args.quality_keyword, ignore_quality_bits = args.ignore_quality_bits)
	
	file_path = aia_data.get_good_quality_file(date = args.date, wavelength = args.wavelength)
	
	if file_path:
		print(file_path)
	else:
		print('No file found!')
