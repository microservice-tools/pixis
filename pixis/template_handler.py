import re
import pathlib
import hashlib
import difflib
import json
from collections import OrderedDict

import jinja2

import pixis.config as cfg
import pixis.openapi as oapi

EXT_REGEX = re.compile('x-.*')
TEMPLATE_CONTEXT = {}


def create_template_context():
    """Creates the template context

    Delegates other functions to create context for template variables
    Default template context has the variables: 'schemas', 'paths', 'base_path', 'cfg'
    Calls Config.IMPLEMENTATION.process() to allow the user to make final changes
    """
    TEMPLATE_CONTEXT['schemas'] = get_schemas_by_name()
    TEMPLATE_CONTEXT['paths'] = get_paths_by_tag()
    TEMPLATE_CONTEXT['base_path'] = get_base_path()
    TEMPLATE_CONTEXT['cfg'] = cfg.Config
    cfg.Config.IMPLEMENTATION.process()


def load_checksums():
    try:
        cfg.Config._checksums = json.loads(pathlib.Path('.pixis.json').read_text())
        print('Found .pixis.json!')
    except FileNotFoundError:
        print('No .pixis.json found')
        return


def save_checksums():
    pathlib.Path('.pixis.json').write_text(json.dumps(cfg.Config._checksums, sort_keys=True, indent=4))
    print('Saved hashes for generated files in .pixis.json')


def emit_template(template_path: str, output_dir: str, output_name: str) -> None:
    """Creates a file using template defined by @template_path into directory defined by @output_dir with filename defined by @output_name

    Args:
        template_path (str): where the template is and what the template file's name is
        output_dir (str): where to output files
        output_name (str): name of output file name
    """
    file_path = pathlib.Path(output_dir) / pathlib.Path(output_name)

    try:  # check for their custom templates
        template_name = pathlib.Path(template_path).name
        template_loader = jinja2.FileSystemLoader(cfg.Config.TEMPLATES)
        env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
        template = env.get_template(template_name)  # template_path is something like: server_flask/model.j2, so we have to do a name comparison here
        print("Generated file [" + file_path + "] from user-defined template")
    except jinja2.exceptions.TemplateNotFound:
        try:  # check for template in Pixis
            template_loader = jinja2.PackageLoader('pixis', 'templates')
            env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
            template = env.get_template(template_path)
        except jinja2.exceptions.TemplateNotFound as err:
            raise ValueError('Template does not exist\n')

    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)  # make directories if it does not already exist
    new_file_text = template.render(TEMPLATE_CONTEXT)
    new_file_checksum = hashlib.md5(new_file_text.encode('utf-8')).hexdigest()

    if is_protected(file_path):
        print("Did not generate [" + str(file_path) + "] (PROTECTED)")
        return

    if cfg.Config.OVERWRITE:
        generate_file(file_path, new_file_text, new_file_checksum)
        print("Generated [" + str(file_path) + "] (OVERWRITE flag set and not PROTECTED)")
        return

    old_file_checksum = cfg.Config._checksums.get(str(file_path))
    cur_file_checksum = None
    cur_file_text = None

    try:
        cur_file_text = file_path.read_text()
        cur_file_checksum = hashlib.md5(cur_file_text.encode('utf-8')).hexdigest()
    except FileNotFoundError:  # Generation is safe, because not overwriting anything
        generate_file(file_path, new_file_text, new_file_checksum)
        print("Generated [" + str(file_path) + "] because file doesn't exist yet")
        return

    if old_file_checksum is None:
        maybe_generate()
        return

    if new_file_checksum == old_file_checksum:
        print('Did not generate [' + str(file_path) + '] (would generate same file as last time)')
        return

    if cur_file_checksum == old_file_checksum:
        generate_file(file_path, new_file_text, new_file_checksum)
        print("Generated [" + str(file_path) + "]. File is unmodified, but something has changed (templates/Pixis/etc)")
        return

    maybe_generate()


def is_protected(file_path):
    # PosixPath('build/server/hello.py') -> PosixPath('/server/hello.py')
    p = pathlib.Path(str(pathlib.Path('/')) + str(file_path.relative_to(*file_path.parts[:1])))
    for s in cfg.Config.PROTECTED:
        if s in str(p):
            return True
        try:
            pattern = re.compile(s)
            if pattern.match(str(p)):
                return True
        except re.error:
            pass

    return False


def maybe_generate(file_path, new_file_text, new_file_checksum):
    for line in difflib.unified_diff(cur_file_text.splitlines(), new_file_text.splitlines(), fromfile=file_path.name + '(current)', tofile=file_path.name + '(new)'):
        print(line)
    overwrite = input('Overwrite file [' + str(file_path) + ']? (y/n) ') + ' '
    if overwrite[0].lower() == 'y':
        generate_file(file_path, new_file_text, new_file_checksum)
        print('Overwrote file [' + str(file_path) + ']')
    else:
        print('Did not overwrite [' + str(file_path) + ']')


def generate_file(path, text, checksum):
    path.write_text(text)
    cfg.Config._checksums[str(path)] = checksum


def get_base_path():
    """Gets the base path

    Returns:
        string of server base path for application
    """
    return cfg.Config.SPEC_DICT['servers'][0]['url']


def get_paths_by_tag():
    """Organizes each path by tag

    Returns:
        dictionary with the tag as key and list of pathlib.Path objects sorted first by url, then by function name
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

    paths_by_tag_sorted = {}
    for tag, paths in paths_by_tag.items():
        paths_by_tag_sorted[tag] = sorted(sorted(paths, key=lambda k: k.function_name), key=lambda k: k.url)

    return OrderedDict(sorted(paths_by_tag_sorted.items()))


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
                        string = 'Inner' * depth
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
            models[schema_name] = oapi.Schema(schema_name, schema_obj)
        else:
            parse_schema(schema_name, schema_obj, 0)

    return models
