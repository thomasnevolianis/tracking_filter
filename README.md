# tracking_filter #

### What is this repository for? ###

A tracking algorithm of given IDs with relaxation factor to adjust the searching range. The algorithm is used to calculate the end-to-end distance of 2 IDs after neural networks are applied in a raw video and a txt file (coordinates) is produced.

Author: Thomas Nevolianis

For help run:  `tracking_filter.py --h`
```
usage: tracking_filter.py [-h] [--relax_factor RELAX_FACTOR]
                          txt_file original_video ID
```
```
This script is a tracking algorithm to filter the undesirable data and take
into consideration only the necessary ones.

positional arguments:
  txt_file              path of the txt file in x, y, width, height
  original_video        path of the original video file
  ID                    an ID

optional arguments:
  -h, --help            show this help message and exit
  --relax_factor RELAX_FACTOR
                        give a relaxation factor
```