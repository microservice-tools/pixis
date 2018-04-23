import re

import codegen.configurations as cfg
from codegen.classes import Path, Model


def init_template_context():
    cfg.TEMPLATE_CONTEXT['schemas'] = get_schemas_by_name()
    cfg.TEMPLATE_CONTEXT['paths'] = get_paths_by_tag()
    cfg.TEMPLATE_CONTEXT['base_path'] = get_base_path()


def get_base_path():
    return cfg.SPEC_DICT['servers'][0]['url']


def get_paths_by_tag():
    paths_by_tag = {}
    methods = ['get', 'put', 'post', 'delete', 'options', 'head', 'patch', 'trace']

    def add_to_paths(paths_by_tag, parent_dict, operation_dict):
        path = Path(parent_dict, operation_dict)
        tag = path.tag
        if tag is None:
            tag = 'default'
        if tag not in paths_by_tag:
            paths_by_tag[tag] = [path]
        else:
            paths_by_tag[tag].append(path)

    for path_url, path_dict in cfg.SPEC_DICT['paths'].items():
        parent_dict = {
            'url': path_url,
            'summary': path_dict.get('summary'),
            'description': path_dict.get('description'),
            'servers': path_dict.get('servers'),
            'parameters': path_dict.get('parameters')
        }
        for key, value in path_dict.items():
            if re.match(cfg.EXT_REGEX, key):
                parent_dict[key] = value
        for method in methods:
            operation_dict = path_dict.get(method)
            if operation_dict is not None:
                parent_dict['method'] = method
                add_to_paths(paths_by_tag, parent_dict, operation_dict)

    return paths_by_tag


def get_schemas_by_name():
    models = {}
    for schema_name, schema in cfg.SPEC_DICT['components']['schemas'].items():
        model = Model(schema_name, schema)
        models[model.name] = model

    return models
