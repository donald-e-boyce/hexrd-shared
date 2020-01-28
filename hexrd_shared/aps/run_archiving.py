"""Sample processing script to build imageseries from scan images

* developed at APS 2019-08
* Modify inputs section as needed
"""
import os
import multiprocessing
import aps

import numpy as np

# ==================== Inputs
# Options to write files.

write_raw = True
write_frame_cache = True
threshold = 15
empty_frames = 1
ncpus = multiprocessing.cpu_count()

# General information about the experiment
# HOME_DIR = "/home/beams/S1IDUSER"  # beams
HOME_DIR = "/clhome/TOMO1"  # orthros

PAR_PATH = os.getcwd()  # orthros

# %%
parfile_name = os.path.join(
    PAR_PATH,
    "fastpar_PUP_AFRL_aug19_FF.par"
)
image_dir = os.path.join(
    HOME_DIR,
    "mnt/s1c/PUP_AFRL_aug19"
)
panels = ("ge1", "ge2", "ge3", "ge4")

# first, calibration samples
#sample_names = [
#'Au_ff', 'Ruby_box_ff', 'Ruby_line_ff',
#]
sample_names = []  # restarting...

# then line scans
lshr_line_names = ['lshr_r6_s%d_line_ff' % i for i in np.arange(7, 14)]
lshr_line_names.append('lshr_r6_ungrip_line_ff')
sample_names += lshr_line_names

# lastly, box scans
lshr_box_names = ['lshr_r6_s%d_box_ff' % i for i in np.arange(0, 14)]
lshr_box_names.append('lshr_r6_ungrip_box_ff')
sample_names += lshr_box_names

# Specific data:  sample/scans to write

pp = aps.ParParser(parfile_name,
                   image_dir=image_dir
)

## # ==================== Process images
params = dict(
    threshold=threshold,
    empty=empty_frames
)

for sample_name in sample_names:
    for scan in pp.scans(sample_name):
        if write_raw:
            yml_names = pp.write_raw(sample_name, [scan, ], panels)
            print("yml files: ", yml_names)

        if write_frame_cache:
            print("INFO:\tusing %d prcesses to export frame-cache files"
                  % ncpus + "'%s_%s'" % (sample_name, scan)
            )
            pool = multiprocessing.Pool(ncpus, aps.process_raw_mp_init, (params, ))
            result = pool.map(aps.process_raw_mp, yml_names)
            pool.close()

# serial version
#     for n in yml_names:
#
#         aps.process_raw(n,
#                         threshold=threshold,
#                         empty=empty_frames
#         )
