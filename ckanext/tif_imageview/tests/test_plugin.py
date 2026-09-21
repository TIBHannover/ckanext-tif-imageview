"""
Tests for plugin.py.

Tests are written using the pytest library (https://docs.pytest.org), and you
should read the testing guidelines in the CKAN docs:
https://docs.ckan.org/en/2.9/contributing/testing.html

To write tests for your extension you should install the pytest-ckan package:

    pip install pytest-ckan

This will allow you to use CKAN specific fixtures on your tests.

For instance, if your test involves database access you can use `clean_db` to
reset the database:

    import pytest

    from ckan.tests import factories

    @pytest.mark.usefixtures("clean_db")
    def test_some_action():

        dataset = factories.Dataset()

        # ...

For functional tests that involve requests to the application, you can use the
`app` fixture:

    from ckan.plugins import toolkit

    def test_some_endpoint(app):

        url = toolkit.url_for('myblueprint.some_endpoint')

        response = app.get(url)

        assert response.status_code == 200


To temporary patch the CKAN configuration for the duration of a test you can use:

    import pytest

    @pytest.mark.ckan_config("ckanext.myext.some_key", "some_value")
    def test_some_action():
        pass
"""
import base64
import io

import pytest
from PIL import Image
from ckan import plugins
from ckan.plugins import toolkit
from werkzeug.exceptions import BadRequest

import ckanext.tif_imageview.plugin as plugin

@pytest.mark.ckan_config("ckan.plugins", "tif_imageview")
@pytest.mark.usefixtures("with_plugins")
@pytest.mark.parametrize(
    "resource, expected",
    [
        ({"format": "TIFF", "url": "image", "url_type": "upload"}, True),
        (
            {
                "format": "",
                "url": "https://example.test/image.TIF?download=1",
                "url_type": "upload",
            },
            True,
        ),
        ({"format": "tif", "url": "image.tif", "url_type": ""}, False),
        ({"format": "", "url_type": "upload"}, False),
    ],
)
def test_can_view_only_supported_uploaded_tiffs(resource, expected):
    image_view = plugins.get_plugin("tif_imageview")

    assert image_view.can_view({"resource": resource}) is expected


@pytest.mark.usefixtures("with_request_context")
def test_convert_requires_resource_id():
    with pytest.raises(BadRequest, match="Missing resource_id"):
        plugin.convert()


def test_convert_uploaded_tiff_to_jpeg(app, monkeypatch, tmp_path):
    source_path = tmp_path / "image.tif"
    Image.new("RGB", (2, 2), color="red").save(source_path, "TIFF")
    resource = {
        "id": "resource-id",
        "url": "image.tif",
        "url_type": "upload",
    }

    monkeypatch.setattr(
        toolkit,
        "get_action",
        lambda _name: lambda _context, _data_dict: resource,
    )
    monkeypatch.setattr(
        plugin.uploader,
        "get_resource_uploader",
        lambda _resource: type(
            "Upload", (), {"get_path": lambda self, _id: str(source_path)}
        )(),
    )

    with app.flask_app.test_request_context(
        method="POST", data={"resource_id": "resource-id"}
    ):
        result = plugin.convert()

    converted = Image.open(io.BytesIO(base64.b64decode(result)))
    assert converted.format == "JPEG"
    assert converted.size == (2, 2)
