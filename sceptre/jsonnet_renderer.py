# -*- coding: utf-8 -*-

"""
sceptre.jsonnet_renderer

This module implements a JsonnetRenderer class, which renders Jsonnet templates.
"""

import json
import yaml
import subprocess


# Jsonnet imports are resolved relative to this directory, which in turn is
# relative to the repository root.
TEMPLATES_DIR = "templates"

# Jsonnet command and associated arguments to render a template
JSONNET_COMMAND = ["jsonnet", "--jpath", TEMPLATES_DIR]


class JsonnetRenderer(object):
    """
    Uses the Jsonnet command to render .jsonnet templates to
    CloudFormation. See https://jsonnet.org/ for more info on Jsonnet.
    """

    @staticmethod
    def _render(template_path, extra_args=[]):
        """
        Low level function to run the jsonnet command as a subprocess.

        :param template_path: Path to the template to render.
        :param extra_args: List of strings to send to the jsonnet command as
            arguments.
        :returns: The output of the jsonnet command, as a string.
        :rtype: str
        """
        subprocess_args = JSONNET_COMMAND + extra_args + [template_path]
        result = subprocess.run(
            subprocess_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            jsonnet_error = result.stderr.decode("utf-8")
            raise RuntimeError(
                f"Execution of {' '.join(subprocess_args)} failed with error:\n{jsonnet_error}"
            )
        return result.stdout.decode("utf-8")

    @staticmethod
    def render_json(template_path, extra_args=[]):
        """
        Renders a jsonnet template to JSON, returning the rendered string.

        :param template_path: Path to the template to render.
        :type template_path: str
        :param extra_args: List of strings to send to the jsonnet command as
            arguments.
        :returns: The json rendered from template_path as a string.
        :rtype: str
        """
        return JsonnetRenderer._render(template_path, extra_args)

    @staticmethod
    def render_python(template_path, extra_args=[]):
        """
        Renders a jsonnet template to a Python object and returns that object.

        :param template_path: Path to the template to render.
        :type template_path: str
        :param extra_args: List of strings to send to the jsonnet command as
            arguments.
        :returns: The body of the Jsonnet template as a Python object.
        :rtype: dict
        """
        rendered_template = JsonnetRenderer.render_json(template_path, extra_args)
        return json.loads(rendered_template)

    @staticmethod
    def render(template_path, extra_args=[]):
        """
        Renders a jsonnet template to YAML, returning the rendered string.

        :param template_path: Path to the template to render.
        :type template_path: str
        :param extra_args: List of strings to send to the jsonnet command as
            arguments.
        :returns: The body of the Jsonnet template in YAML format.
        :rtype: str
        """
        template_obj = JsonnetRenderer.render_python(template_path, extra_args)
        return yaml.safe_dump(template_obj)
