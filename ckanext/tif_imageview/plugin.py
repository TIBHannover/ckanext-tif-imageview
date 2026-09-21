import base64
import io
from urllib.parse import urlsplit

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from six import text_type
from flask import Blueprint, request
from PIL import Image
import ckan.lib.uploader as uploader

ignore_empty = plugins.toolkit.get_validator('ignore_empty')


def convert():
    resource_id = request.form.get('resource_id')
    if not resource_id:
        toolkit.abort(400, 'Missing resource_id')

    context = {'user': getattr(toolkit.g, 'user', None)}
    rsc = toolkit.get_action('resource_show')(context, {'id': resource_id})
    if rsc.get('url_type') != 'upload':
        toolkit.abort(400, 'Only uploaded TIFF resources can be converted')

    upload = uploader.get_resource_uploader(rsc)
    filepath = upload.get_path(rsc['id'])
    with open(filepath, 'rb') as source:
        image_data = source.read()

    img = Image.open(io.BytesIO(image_data))
    output = io.BytesIO()
    img.convert('RGB').save(output, 'JPEG')
    output.seek(0)
    return base64.b64encode(output.getvalue()).decode()


class TifImageviewPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IBlueprint)



    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'theme/templates')
        toolkit.add_public_directory(config_, 'public')
        
        
    def info(self):
        return {'name': 'tif_imageview',
            'title': plugins.toolkit._('TIF Viewer'),
            'schema': {'tif_url': [ignore_empty, text_type]},
            'iframed': False,
            'icon': 'link',
            'always_available': True,
            'default_title': plugins.toolkit._('TIF Viewer'),
        }
    
    def can_view(self, data_dict):
        resource = data_dict['resource']
        if resource.get('url_type') != 'upload':
            return False

        image_format = resource.get('format', '').lower()
        path = urlsplit(resource.get('url', '')).path.lower()
        return image_format in {'tif', 'tiff'} or path.endswith(
            ('.tif', '.tiff')
        )

    def view_template(self, context, data_dict):
        return 'tif_view.html'

    def form_template(self, context, data_dict):
        return 'tif_form.html'

    def get_blueprint(self):

        blueprint = Blueprint(self.name, self.__module__)
        blueprint.template_folder = u'templates'
        blueprint.add_url_rule(
            u'/tif_view/convert',
            u'convert',
            convert,
            methods=['POST']
            )
        
        return blueprint
