"""
Handles everything related to the template context and emitting templates
"""


import re
import os

import jinja2

import pixis.config as cfg
import pixis.openapi as oapi

EXT_REGEX = re.compile('x-.*')
TEMPLATE_CONTEXT = {}


def create_template_context():
    TEMPLATE_CONTEXT['schemas'] = get_schemas_by_name()
    TEMPLATE_CONTEXT['paths'] = get_paths_by_tag()
    TEMPLATE_CONTEXT['base_path'] = get_base_path()
    TEMPLATE_CONTEXT['cfg'] = cfg.Config
    cfg.Config.IMPLEMENTATION.process()


def emit_template(template_path, output_dir, output_name):
    try:
        # check for their custom templates
        template_name = template_path.split('/')[-1]
        template_loader = jinja2.FileSystemLoader(os.getcwd() + os.path.sep + cfg.Config.TEMPLATES)
        env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
        template = env.get_template(template_name)  # template_path is something like: server_flask/model.j2, so we have to do a name comparison here
        print("outputed file \" " + output_name + " \" from user defined template")
    except jinja2.exceptions.TemplateNotFound:
        # check for template in our package
        try:
            template_loader = jinja2.PackageLoader('pixis', 'templates')
            env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
            template = env.get_template(template_path)
        except jinja2.exceptions.TemplateNotFound as err:
            raise ValueError('Template does not exist\n')

    # env.globals['cfg'] = cfg.Config
    output_file = output_dir + os.path.sep + output_name

    directory = os.path.dirname(output_file)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(output_file, 'w') as outfile:
        outfile.write(template.render(TEMPLATE_CONTEXT))


def get_base_path():
    return cfg.Config.SPEC_DICT['servers'][0]['url']


def get_paths_by_tag():
    paths_by_tag = {}
    methods = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']

    def add_to_paths(paths_by_tag, parent_dict, operation_dict):
        path = oapi.Path(parent_dict, operation_dict)
        tag = path.tag
        if tag is None:
            tag = 'default'
        if tag not in paths_by_tag:
            paths_by_tag[tag] = [path]
        else:
            paths_by_tag[tag].append(path)

    for path_url, path_dict in cfg.Config.SPEC_DICT['paths'].items():
        parent_dict = {
            'url': path_url,
            'summary': path_dict.get('summary'),
            'description': path_dict.get('description'),
            'servers': path_dict.get('servers'),
            'parameters': path_dict.get('parameters')
        }
        for key, value in path_dict.items():
            if re.match(EXT_REGEX, key):
                parent_dict[key] = value
        for method in methods:
            operation_dict = path_dict.get(method)
            if operation_dict is not None:
                parent_dict['method'] = method
                add_to_paths(paths_by_tag, parent_dict, operation_dict)

    return paths_by_tag


def get_schemas_by_name():
    models = {}
    if 'components' in cfg.Config.SPEC_DICT and 'schemas' in cfg.Config.SPEC_DICT['components']:
        for schema_name, schema in cfg.Config.SPEC_DICT['components']['schemas'].items():
            model = oapi.Model(schema_name, schema)
            models[model.name] = model

    return models
