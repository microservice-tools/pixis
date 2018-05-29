"""
Handles everything related to the template context and emitting templates
"""


import re
from pathlib import Path
import hashlib
import difflib
import json

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


def emit_template(template_path: str, output_dir: str, output_name: str) -> None:
    try:  # check for their custom templates
        template_name = Path(template_path).name
        template_loader = jinja2.FileSystemLoader(cfg.Config.TEMPLATES)
        env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
        template = env.get_template(template_name)  # template_path is something like: server_flask/model.j2, so we have to do a name comparison here
        print("Output file \" " + output_name + " \" from user-defined template")
    except jinja2.exceptions.TemplateNotFound:
        try:  # check for template in Pixis
            template_loader = jinja2.PackageLoader('pixis', 'templates')
            env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
            template = env.get_template(template_path)
        except jinja2.exceptions.TemplateNotFound as err:
            raise ValueError('Template does not exist\n')

    Path(output_dir).mkdir(parents=True, exist_ok=True)  # make directories if it does not already exist
    output_file = Path(output_dir) / Path(output_name)
    new_file_str = template.render(TEMPLATE_CONTEXT)

    if generate_file(output_file, new_file_str):
        with output_file.open('w') as out_file:
            out_file.write(new_file_str)
            cfg.Config.HASH_DICT[output_name] = hashlib.md5(new_file_str.encode('utf-8')).hexdigest()

def generate_file(file_path, file_str):
    overwrite = "n"
    hash_dict = cfg.Config.HASH_DICT
    if file_path.is_file():
        with file_path.open('r') as current_file:
            current_file_str = current_file.read()
            current_hash = hashlib.md5(current_file_str.encode('utf-8')).hexdigest()
            if file_path.name not in hash_dict or current_hash != hash_dict[file_path.name]:
                for line in difflib.unified_diff(current_file_str.splitlines(), file_str.splitlines(),
                                                 fromfile='current file', tofile='new file'):
                    print(line)
                overwrite = input("You have modified " + file_path.name + ". Do you want to overwrite (y/n)? ")
                print('Overwriting file...' if overwrite[0].lower() == 'y' else 'Original file kept')

    if overwrite[0].lower() == 'y' or not file_path.is_file():
        return True
    else:
        return False

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

    def parse_schema(schema_name, schema_obj, depth):
        if schema_obj.get('$ref') is None:
            attr_type = schema_obj.get('type')
            if attr_type == 'array':
                depth = depth + 1
                parse_schema(schema_name, schema_obj.get('items'), depth)
            elif attr_type == 'object':
                models[schema_name] = oapi.Schema(schema_name, schema_obj)
                if schema_obj.get('properties') is not None:
                    for attr_name, attr_obj in schema_obj.get('properties').items():
                        string = 'Inner'*depth
                        parse_schema(schema_name + string + attr_name.capitalize(), attr_obj, 0)
                    
    def attr_primitive(schema_obj):
        if schema_obj.get('$ref') is None:
            attr_type = schema_obj.get('type')
            if attr_type == "string" or attr_type == "integer" or attr_type == "boolean":
                return True
            elif attr_type == "object":
                return False
            else:
                attr_primitive(schema_obj.get('items'))
        return True

    for schema_name, schema_obj in cfg.Config.SPEC_DICT['components']['schemas'].items():
        attr_is_primitive = attr_primitive(schema_obj)
        if attr_is_primitive is True:
            models[schema_name] = oapi.Schema(schema_name,schema_obj)
        else: 
            parse_schema(schema_name, schema_obj, 0)

    return models