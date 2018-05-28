"""
Handles everything related to the template context and emitting templates
"""


import re
from pathlib import Path

import jinja2

import pixis.config as cfg
import pixis.openapi as oapi

EXT_REGEX = re.compile('x-.*')
TEMPLATE_CONTEXT = {}


def create_template_context():
    """
    Creates the template context for 'schemas', 'paths', and 'base_path' based on the specification file and the 'cfg' variables defined in config.py

    Also modifies the template context defaults based on user-defined implementation and/or framework specific type mappings, name case mappings and serialization
    """
    TEMPLATE_CONTEXT['schemas'] = get_schemas_by_name()
    TEMPLATE_CONTEXT['paths'] = get_paths_by_tag()
    TEMPLATE_CONTEXT['base_path'] = get_base_path()
    TEMPLATE_CONTEXT['cfg'] = cfg.Config
    cfg.Config.IMPLEMENTATION.process()


def emit_template(template_path, output_dir, output_name):
    """
    Creates a file using template defined by 'template_path' into directory defined by 'output_dir' with the name defined by 'output_name'

    Args:
        template_path (str): template path to use to obtain template for file output
        output_dir (str): name of output directory
        output_name (str): name of output file name
    """
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

    with output_file.open('w') as outfile:
        outfile.write(template.render(TEMPLATE_CONTEXT))


def get_base_path():
    """
    Gets the base path from the specification file

    Returns:
        string of server base path of application
    """
    return cfg.Config.SPEC_DICT['servers'][0]['url']


def get_paths_by_tag():
    """
    Gets the paths and organizes it by 'tag' with attributes of each Path object including method, parameters and operationId from the specification file

    Returns:
        dictionary with the tag as key and list of Path objects
    """
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
    """
    Get schemas dictionary and accesses attributes of schema by name including dependencies, type and properties

    Returns:
        dictionary of schemas with the schema name as the key and Schema object as the value
    """
    models = {}

    def parse_schema(schema_name, schema_obj, depth):
        """
        Create Schema objects within Schema objects and recursively

        Args:
            schema_name (str): name of schema object
            schema_obj (Dict): attributes of schema object
            depth (int): value of the depth schema object within arrays
                For example, an array of Schema objects will have a depth of '1'. An array of an array of Schema objects will have a depth of '2'.
        """
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
        """
        Determines if schema object type is primitive. If type is 'string', 'integer', or 'boolean', schema object is primitive. If schema object type is object, schema object is not primitive.
        
        Recursively determines within type of 'items' of arrays within arrays of schema_obj to determine if the base is primitive
        
        Args:
            schema_obj (Dict): schema object attributes dictionary

        Returns:
            True if 'schema_obj' is primitive. False, otherwise
        """
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