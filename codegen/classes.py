import re

import codegen.configurations as cfg


class OpenAPI3():
    def get_reference(self, dikt):
        if '$ref' not in dikt:
            return dikt

        ref_string = dikt['$ref']
        ref_path = ref_string.split('/')

        ref = cfg.SPEC_DICT[ref_path[1]][ref_path[2]][ref_path[3]]
        return ref

    def get_extensions(self, dikt):
        extensions = {}

        for key, value in dikt.items():
            if cfg.EXT_REGEX.match(key):
                extensions[key] = value

        return extensions

    def get_contents(self, dikt):
        content_dict = dikt.get('content')
        if content_dict is None:
            return []

        contents = []
        for _format, info in content_dict.items():
            contents.append(Content(_format, info))

        return contents

    def get_content_formats(self, dikt):
        contents = self.get_contents(dikt)
        if contents is None:
            return []

        formats = []
        for content in contents:
            formats.append(content.format)

        return formats

    def get_content_types(self, dikt):
        contents = self.get_contents(dikt)
        if contents is None:
            return []

        types = []
        for content in contents:
            types.append(content.type)

        return types

    def get_schema_type(self, dikt):
        schema_dict = dikt.get('schema')
        if schema_dict is None:
            return None

        def get_type(schema_dict, depth=0):
            ref = schema_dict.get('$ref')
            if ref is not None:
                s = ref.split('/')[3]
                for _ in range(depth):
                    s += cfg.TYPE_MAPPINGS[cfg.LANGUAGE]['>']
                return s
            if schema_dict.get('type') == 'array':
                return cfg.TYPE_MAPPINGS[cfg.LANGUAGE]['array'] + cfg.TYPE_MAPPINGS[cfg.LANGUAGE]['<'] + get_type(schema_dict['items'], depth + 1)
            # TODO OBJECTS
            # TODO FORMAT
            s = cfg.TYPE_MAPPINGS[cfg.LANGUAGE][schema_dict['type']]
            for _ in range(depth):
                s += cfg.TYPE_MAPPINGS[cfg.LANGUAGE]['>']
            return s

        """
        def get_type(schema_dict, depth=0):
            ref = schema_dict.get('$ref')
            if ref is not None:
                s = ref.split('/')[3]
                for _ in range(depth):
                    s += '>'
                return s
            if schema_dict.get('type') == 'array':
                return 'array<' + get_type(schema_dict['items'], depth + 1)
            # TODO OBJECTS
            # TODO FORMAT
            s = schema_dict['type']
            for _ in range(depth):
                s += '>'
            return s
        """

        return get_type(schema_dict)

    def to_boolean(self, s):
        if s is None:
            return False  # or should we return None?
        if type(s) is bool:
            return s
        if s.lower() == 'true':
            return True
        return False


class Path(OpenAPI3):
    """
    description, summary, servers, parameters, extensions can be from higher level
    paths have references, but not sure if we're going to support it because seems like openapi3 doesn't support it either?
    highest level extensions aren't supported (i.e. paths -> ^x-)
    """

    def __init__(self, parent_dict, operation_dict):
        path_dict = self.merge_dicts(parent_dict, operation_dict)
        self.url = path_dict['url']
        self.tag = self.get_tag(path_dict)
        self.method = path_dict['method']
        self.function_name = path_dict.get('operationId')
        self.parameters = self.get_parameters(path_dict)  # array<Parameter>
        self.parameters_in = self.get_parameters_in()  # set<string>
        self.request_body = self.get_request_body(path_dict)
        self.responses = self.get_responses(path_dict)  # REQUIRED {<string>, Response}
        self.response_formats = self.get_response_formats()  # set<string>
        self.dependencies = self.get_dependencies(path_dict)  # set<string>

        # TODO
        self.summary = path_dict.get('summary')
        self.description = path_dict.get('description')
        self.externalDocs = path_dict.get('externalDocs')
        self.callbacks = path_dict.get('callbacks')
        self.security = path_dict.get('security')
        self.servers = path_dict.get('servers')
        self.deprecated = self.to_boolean(path_dict.get('deprecated'))
        self.extensions = self.get_extensions(path_dict)

    def get_dependencies(self, path_dict):

        def get_dependency(dikt):
            schema_dict = dikt.get('schema')
            if schema_dict is None:
                schema_dict = dikt.get('items')
                if schema_dict is None:
                    return None

            ref = schema_dict.get('$ref')
            if ref is not None:
                return ref.split('/')[3]

            if schema_dict.get('type') == 'array':
                return get_dependency(schema_dict)

            return None

        dependencies = set()

        responses_dict = path_dict.get('responses')
        if responses_dict is not None:
            for code, dikt in responses_dict.items():
                response = self.get_reference(dikt)
                if 'content' in response:
                    for _format, content in response['content'].items():
                        dependencies.add(get_dependency(content))

        request_body_dict = path_dict.get('requestBody')
        if request_body_dict is not None:
            request_body = self.get_reference(request_body_dict)
            for _format, content in request_body['content'].items():
                dependencies.add(get_dependency(content))

        if None in dependencies:
            dependencies.remove(None)

        return dependencies

    def get_tag(self, path_dict):
        tags = path_dict.get('tags')
        if tags is None:
            return None
        return tags[0]

    def get_response_formats(self):
        # self.responses will never be None
        response_formats = set()

        for code, response in self.responses.items():
            for _format in response.formats:
                response_formats.add(_format)

        return response_formats

    def get_request_body(self, path_dict):
        request_body_dict = path_dict.get('requestBody')
        if request_body_dict is None:
            return None

        return RequestBody(request_body_dict)

    def get_parameters_in(self):
        if self.parameters is None:
            return set()

        parameters_in = set()
        for parameter in self.parameters:
            parameters_in.add(parameter._in)

        return parameters_in

    def get_parameters(self, path_dict):
        params_list = path_dict.get('parameters')
        if params_list is None:
            return []

        parameters = []
        for param_dict in params_list:
            parameters.append(Parameter(param_dict))

        return parameters

    def get_responses(self, path_dict):
        resp_dict = path_dict.get('responses')

        responses = {}
        for code, response_dict in resp_dict.items():
            responses[code] = Response(code, response_dict)

        return responses

    def merge_dicts(self, fallback_dict, priority_dict):
        dikt = {}

        for key, value in fallback_dict.items():
            if re.match(cfg.EXT_REGEX, key):
                dikt[key] = value

        for key, value in priority_dict.items():
            dikt[key] = value

        fallback_keys = ['summary', 'description', 'servers', 'method', 'url']
        for key in fallback_keys:
            if key not in dikt:
                dikt[key] = fallback_dict.get(key)

        fallback_parameters = fallback_dict.get('parameters')
        priority_parameters = dikt.get('parameters')

        if priority_parameters is None:
            dikt['parameters'] = fallback_parameters

        if priority_parameters is not None and fallback_parameters is not None:
            unique_parameters = set()
            for item in priority_parameters:
                priority_parameter_dict = self.get_reference(item)
                unique_parameters.add((priority_parameter_dict['name'], priority_parameter_dict['in']))

            for item in fallback_parameters:
                fallback_parameter_dict = self.get_reference(item)
                key = (fallback_parameter_dict['name'], fallback_parameter_dict['in'])
                if key not in unique_parameters:
                    dikt['parameters'].append(fallback_parameter_dict)

        return dikt


class Content(OpenAPI3):
    def __init__(self, _format, content_dict):
        self.format = _format
        self.type = self.get_schema_type(content_dict)

        # TODO
        self.example = content_dict.get('example')
        self.examples = content_dict.get('examples')
        self.encoding = content_dict.get('encoding')
        self.extensions = self.get_extensions(content_dict)


class RequestBody(OpenAPI3):
    def __init__(self, dikt):
        request_body_dict = self.get_reference(dikt)

        self.formats = self.get_content_formats(request_body_dict)  # array<string>
        self.types = self.get_content_types(request_body_dict)  # array<string>
        self.contents = self.get_contents(request_body_dict)  # array<Content>

        # TODO
        self.required = self.to_boolean(request_body_dict.get('required'))
        self.description = request_body_dict.get('description')
        self.extensions = self.get_extensions(request_body_dict)


class Response(OpenAPI3):
    def __init__(self, response_code, dikt):
        response_dict = self.get_reference(dikt)

        self.code = response_code
        self.formats = self.get_content_formats(response_dict)  # array<string>
        self.types = self.get_content_types(response_dict)  # array<string>
        self.contents = self.get_contents(response_dict)  # array<Content>

        # TODO
        self.description = response_dict.get('description')  # REQUIRED
        self.headers = response_dict.get('headers')
        self.extensions = self.get_extensions(response_dict)


class Parameter(OpenAPI3):
    def __init__(self, dikt):
        parameter_dict = self.get_reference(dikt)

        self.name = parameter_dict.get('name')  # REQUIRED
        self._in = parameter_dict.get('in')  # REQUIRED
        self.required = self.to_boolean(parameter_dict.get('required'))
        self.type = self.get_schema_type(parameter_dict)

        # TODO
        self.description = parameter_dict.get('description')
        self.style = parameter_dict.get('style')
        self.example = parameter_dict.get('example')
        self.examples = parameter_dict.get('examples')
        self.deprecated = self.to_boolean(parameter_dict.get('deprecated'))
        self.allowEmptyValue = self.to_boolean(parameter_dict.get('allowEmptyValue'))
        self.explode = self.to_boolean(parameter_dict.get('explode'))
        self.allowReserved = self.to_boolean(parameter_dict.get('allowReserved'))
        self.extensions = self.get_extensions(parameter_dict)


class Model:
    def __init__(self, name, schema_obj):
        self.name = name
        # key is filename, value is class that is being imported. **NOT SURE IF THIS WILL BE KEPT**
        self.dependencies = getDeps(schema_obj)
        self.properties = getProperties(schema_obj)  # dictionary with key is property name, value is property type
        self.hasEnums = hasEnums(schema_obj)

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)


def hasEnums(schema_obj):
    for attribute_name, attribute_dikt in schema_obj['properties'].items():
        hasEnums = attribute_dikt.get('enum')
        if hasEnums is not None:
            return True

    return False


def getDeps(schema_obj):

    deps = []

    for attribute_name, attribute_dikt in schema_obj['properties'].items():
        attr_deps = getDepByAttr(attribute_dikt)
        deps = deps + attr_deps

    return deps


def getDepByAttr(attribute_dikt):
    depsByAttr = []

    ref = attribute_dikt.get('$ref')
    if ref is not None:
        ref = ref[ref.rfind('/') + 1:]
        depsByAttr.append(ref)

    elif attribute_dikt['type'] == 'array':
        depsByAttr = depsByAttr + getDepByAttr(attribute_dikt['items'])

    return depsByAttr


class Property:
    def __init__(self, name, property_obj, requiredList):
        self.name = name
        self.type = getType(property_obj, 0)
        self.isRequired = isRequired(name, requiredList)
        # returns None if no enums associated with property, otherwise return a list
        self.enums = getEnums(property_obj)

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)


class Enum:
    def __init__(self, attributes):
        self.attributes = attributes

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)


def getType(schema_obj, depth):

    if '$ref' in schema_obj:
        s = schema_obj['$ref'].split('/')[3]
        for x in range(depth):
            s += '>'
        return s

    if schema_obj['type'] == 'array':
        return 'array<' + getType(schema_obj['items'], depth + 1)

    # s = typeMapping[schema_obj.type]
    type_format = getattr(schema_obj, 'format', None)
    if type_format is not None:
        s = type_format
    else:
        s = schema_obj['type']

    for x in range(depth):
        s += '>'
    return s


def getEnums(attributes):

    enumList = attributes.get('enum')

    return enumList


def isRequired(attribute_name, requiredList):
    if requiredList is None:
        return False
    elif attribute_name in requiredList:
        return True
    else:
        return False


def getProperties(schema_obj):
    properties = []
    for attribute_name, attribute_dikt in schema_obj['properties'].items():
        property = Property(attribute_name, attribute_dikt, schema_obj.get('required'))
        properties.append(property)

    return properties
