# Steps to produce the EPN-TAP parameters for the year 2025

## Download the level1 SDO files

On the sdo3 server, run the following commands


``` bash
sdo /opt/scripts/download_aia_science.py --wavelength 193 --start-date 2025-02-01 --end-date 2026-02-01 --cadence "6 h" --time-margin "1 h"

sdo /opt/scripts/download_hmi_science.py --start-date 2025-02-01 --end-date 2026-02-01 --cadence '6 h' --time-margin '1 h'
```

## Preprocess the SDO files

On the yama server, run the following commands

``` bash
for m in {02..12}; do
   /home/benjmam/sdo-preprocessing/get_aia_science_level2.py --output-directory /scratch/benjmam/data/aia_science_level2/0193/ /data/SDO/AIA_HMI_1h_synoptic/aia.lev1/0193/2025/$m/*/*.fits &> get_aia_science_level2.2025.$m.log &
done

/home/benjmam/sdo-preprocessing/get_aia_science_level2.py --output-directory /scratch/benjmam/data/aia_science_level2/0193/ /data/SDO/AIA_HMI_1h_synoptic/aia.lev1/0193/2026/01/*/*.fits &> get_aia_science_level2.2026.01.log

for m in {02..12}; do
   /home/benjmam/sdo-preprocessing/get_hmi_science_level1_5.py --output-directory /scratch/benjmam/data/hmi_science_level1_5/magnetogram/ /data/SDO/AIA_HMI_1h_synoptic/hmi.m_45s/2025/$m/*/*.fits &> get_hmi_science_level1_5.2025.$m.log &
done

/home/benjmam/sdo-preprocessing/get_hmi_science_level1_5.py --output-directory /scratch/benjmam/data/hmi_science_level1_5/magnetogram/ /data/SDO/AIA_HMI_1h_synoptic/hmi.m_45s/2026/01/*/*.fits &> get_hmi_science_level1_5.2026.01.log
```

## Copy the preprocessed SDO files to the sdo3 server

On the yama server, run the following commands


``` bash
ssh sdo3  'sudo mkdir /data/sdo/aia_science_level2/0193/2025 && sudo chown benjmam: /data/sdo/aia_science_level2/0193/2025'

rsync -aPv /scratch/benjmam/data/aia_science_level2/0193/2025/ sdo3:/data/sdo/aia_science_level2/0193/2025

ssh sdo3  'sudo chown -R sdo: /data/sdo/aia_science_level2/0193/2025/'

ssh sdo3  'sudo mkdir /data/sdo/hmi_science_level1_5/magnetogram/2025 && sudo chown benjmam: /data/sdo/hmi_science_level1_5/magnetogram/2025'

rsync -aPv /scratch/benjmam/data/hmi_science_level1_5/magnetogram/2025/ sdo3:/data/sdo/hmi_science_level1_5/magnetogram/2025

ssh sdo3  'sudo chown -R sdo: /data/sdo/hmi_science_level1_5/magnetogram/2025/'
```

## Create the TAP parameters

See the end of the previous year log file to know the list of files for the --tracked-ch-maps parameter

On the yama server, run the following commands

``` bash
nohup /home/benjmam/spoca4tap/scripts/rob_spoca_ch_pipeline.py \
--config-file /home/benjmam/spoca4tap/configs/rob_spoca_ch.ini \
--start-date 2025-01-04 \
--end-date 2026-01-04
--interval 6
--regions-colors longlived_regions_colors.2025.txt \
--tracked-ch-maps /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250101_000000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250101_060000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250101_120000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250101_180000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250102_000000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250102_060000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250102_120000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250102_180000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250103_000000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250103_060000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250103_120000.ch_map.fits /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/20250103_180000.ch_map.fits \
&> rob_spoca_ch_pipeline.2025.log &
```

## Create the provenance files

On the yama server, edit the scipt /scratch/benjmam/spoca4tap/rob_spoca_ch/create_provenance_script.py to set the year to 2025 in `for activity_log in ACTIVITY_LOGS_DIR.glob("get_cleaned_map.2024*"):`

Then run the following commands

``` bash
/scratch/benjmam/spoca4tap/rob_spoca_ch/create_provenance_script.py > /scratch/benjmam/spoca4tap/rob_spoca_ch/create_provenance.sh

parallel -j 20 < /scratch/benjmam/spoca4tap/rob_spoca_ch/create_provenance.sh
```

## Copy the product and byproduct files to the spoca server

On the yama server, run the following commands

``` bash
rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/tap_parameters/2025* spoca:/data/spoca/spoca4tap/rob_spoca_ch/tap_parameters/

rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/ch_map/2025* spoca:/data/spoca/spoca4tap/rob_spoca_ch/ch_map/

rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/ch_map_overlay/2025* spoca:/data/spoca/spoca4tap/rob_spoca_ch/ch_map_overlay/

rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/provenance/2025* spoca:/data/spoca/spoca4tap/rob_spoca_ch/provenance/

rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/segmentation_map/2025* /scratch/benjmam/spoca4tap/rob_spoca_ch/segmentation_map/2026* spoca:/data/spoca/spoca4tap/rob_spoca_ch/segmentation_map/

rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/2025* /scratch/benjmam/spoca4tap/rob_spoca_ch/full_ch_map/2026* spoca:/data/spoca/spoca4tap/rob_spoca_ch/full_ch_map/

rsync -aPv /scratch/benjmam/spoca4tap/rob_spoca_ch/activity_log/ spoca:/data/spoca/spoca4tap/rob_spoca_ch/activity_log/

scp -p /scratch/benjmam/spoca4tap/rob_spoca_ch/longlived_regions_colors.2025.txt /scratch/benjmam/spoca4tap/rob_spoca_ch/rob_spoca_ch_pipeline.2025.log spoca:/data/spoca/spoca4tap/rob_spoca_ch/
```
