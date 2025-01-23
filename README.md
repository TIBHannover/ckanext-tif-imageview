
[![CI](https://github.com/TIBHannover/ckanext-tif-imageview/actions/workflows/test.yml/badge.svg)](https://github.com/TIBHannover/ckanext-tif-imageview/actions/workflows/test.yml)

# ckanext-tif-imageview

The CKAN extension for TIFF images preview. 

The plugin **tif_imageview** converts the target tif image to the jpeg format for showing the preview of the image. It does not change or replace the original tif image. 


## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
|  2.9 | Yes    |
| earlier | NoT Tested |           |



## Installation

To install ckanext-tif-imageview:

1. Activate your CKAN virtual environment and install the extension:

        > . /usr/lib/ckan/default/bin/activate
        > pip install ckanext-tif-imageview


2. OR,  Clone the source and install it on the virtualenv

        git clone https://github.com/TIBHannover/ckanext-tif-imageview.git
        cd ckanext-tif-imageview
        pip install -e .
        pip install -r requirements.txt

3. Add `tif_imageview` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Nginx on Ubuntu:

        sudo service nginx reload


## Config settings

Modify ckan.ini (/etc/ckan/default/)

	# add the plugin to:
    ckan.views.default_views



