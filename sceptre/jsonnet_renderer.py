# -*- coding: utf-8 -*-

"""
sceptre.jsonnet_renderer

This module implements a JsonnetRenderer class, which renders Jsonnet templates.
"""

import os
import _jsonnet
import json
import functools


class JsonnetRenderer(object):
    """
    Uses the Jsonnet Python bindings to render .jsonnet templates to
    CloudFormation. See https://jsonnet.org/ref/bindings.html#python_api for
    more info on the Jsonnet Python bindings.
    """
    @staticmethod
    def try_path(template_dir, import_path):
        """
        Try to import a file given by `import_path`, relative to
        `template_dir`. Helper function for import_callback.

        :param template_dir: The directory containing the template.
        :type template_dir: str
        :param import_path: The requested path to import, relative to
               template_dir.
        :returns: The full path to the imported file, and the contents of that
                  file.
        :rtype: (str, str)
        """
        if not import_path:
            raise RuntimeError('Got invalid filename (empty string).')
        if import_path[0] == '/':
            full_path = import_path
        else:
            full_path = os.path.join(template_dir, import_path)
        if full_path[-1] == '/':
            raise RuntimeError('Attempted to import a directory')

        if not os.path.isfile(full_path):
            return full_path, None
        with open(full_path) as f:
            return full_path, f.read()

    @staticmethod
    def import_callback(sceptre_user_data, template_dir, import_path):
        """
        Callback function ran when a Jsonnet template uses the 'import'
        keyword. Treats 'sceptre_user_data' as a special import for the user
        data defined in the template config.

        :param template_dir: The directory containing the template.
        :type template_dir: str
        :param import_path: The requested path to import, relative to
               template_dir.
        :type import_path: str
        :param sceptre_user_data: A dictionary of arbitrary data to be made
               importable in Jsonnet through `import 'sceptre_user_data';`
        :type sceptre_user_data: dict
        :returns: The full path to the imported file, and the contents of that
                  file.
        :rtype: (str, str)
        """
        if import_path == 'sceptre_user_data':
            return 'sceptre_user_data', json.dumps(sceptre_user_data)
        full_path, content = JsonnetRenderer.try_path(template_dir, import_path)
        if content:
            return full_path, content
        raise RuntimeError('File not found')

    @staticmethod
    def render(template_dir, filename, sceptre_user_data):
        """
        Renders a jsonnet template, returning the rendered string.

        :param template_dir: The directory containing the template.
        :type template_dir: str
        :param filename: The name of the template file.
        :type filename: str
        :param sceptre_user_data: A dictionary of arbitrary data to be made
               importable in Jsonnet through `import 'sceptre_user_data';`
        :type sceptre_user_data: dict
        :returns: The body of the CloudFormation template.
        :rtype: str
        """
        import_callback = functools.partial(
                JsonnetRenderer.import_callback,
                sceptre_user_data)
        body = _jsonnet.evaluate_file(
            os.path.join(template_dir, filename),
            import_callback=import_callback,
        )
        return body
