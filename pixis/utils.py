import collections  # for OrderedDict
import os

import jinja2

from pixis.config import Config
from pixis.template_context import TEMPLATE_CONTEXT

"""
entrypoints into our code generation, for us and users
"""

iterators_mapping = collections.OrderedDict()
iterator_functions_mapping = collections.OrderedDict()


def stage_iterator(x_iterator, x_iterator_functions):
    iterator_name = x_iterator.__name__
    iterators_mapping[iterator_name] = x_iterator
    iterator_functions_mapping[iterator_name] = x_iterator_functions


def run_iterators():
    for iterator_name, iterator in iterators_mapping.items():
        iterator(iterator_functions_mapping[iterator_name])


def emit_template(template_path, output_dir, output_name):
    try:
        # check for their custom templates
        template_name = template_path.split('/')[-1]
        template_loader = jinja2.FileSystemLoader(os.getcwd() + os.path.sep + Config.TEMPLATES)
        env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
        template = env.get_template(template_name)  # template_path is something like: flask_server/model.j2, so we have to do a name comparison here
        print("outputed file \" " + output_name + " \" from user defined template")
    except jinja2.exceptions.TemplateNotFound:
        # check for template in our package
        try:
            template_loader = jinja2.PackageLoader('pixis', 'templates')
            env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
            template = env.get_template(template_path)
        except jinja2.exceptions.TemplateNotFound as err:
            raise ValueError('Template does not exist\n' + err)

    # env.globals['cfg'] = Config
    output_file = output_dir + os.path.sep + output_name

    directory = os.path.dirname(output_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(output_file, 'w') as outfile:
        outfile.write(template.render(TEMPLATE_CONTEXT))
