import re

from pixis.config import Config

EXT_REGEX = re.compile('x-.*')


class OpenAPI():
    def get_reference(self, dikt):
        if '$ref' not in dikt:
            return dikt

        ref_string = dikt['$ref']
        ref_path = ref_string.split('/')

        ref = Config.SPEC_DICT[ref_path[1]][ref_path[2]][ref_path[3]]
        return ref

    def get_extensions(self, dikt):
        extensions = {}

        for key, value in dikt.items():
            if re.match(EXT_REGEX, key):
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

        return self.get_type(schema_dict)

    def get_type(self, schema_dict, depth=0):
        ref = schema_dict.get('$ref')
        if ref is not None:
            s = ref.split('/')[3]
            for _ in range(depth):
                s += Config.TYPE_MAPPINGS[Config.IMPLEMENTATION]['>']
            return s
        if schema_dict.get('type') == 'array':
            return Config.TYPE_MAPPINGS[Config.IMPLEMENTATION]['array'] + Config.TYPE_MAPPINGS[Config.IMPLEMENTATION]['<'] + self.get_type(schema_dict['items'], depth + 1)
        # TODO OBJECTS
        # KeyError if schema doesn't have 'type' attribute
        _format = schema_dict.get('format')
        if _format is not None:
            s = Config.TYPE_MAPPINGS[Config.IMPLEMENTATION][_format]
        else:
            s = Config.TYPE_MAPPINGS[Config.IMPLEMENTATION][schema_dict['type']]
        for _ in range(depth):
            s += Config.TYPE_MAPPINGS[Config.IMPLEMENTATION]['>']
        return s

    def to_boolean(self, s):
        if s is None:
            return False
        if type(s) is bool:
            return s
        if s.lower() == 'true':
            return True
        return False

    def __repr__(self):
        return self.to_str()

    def to_str(self):
        return str(self.__dict__)


class Path(OpenAPI):
    """
    description, summary, servers, parameters, extensions can be from higher level
    paths have references, but not sure if we're going to support it because seems like OpenAPI doesn't support it either?
    highest level extensions aren't supported (i.e. paths -> ^x-)
    """

    def __init__(self, parent_dict, operation_dict):
        path_dict = self.merge_dicts(parent_dict, operation_dict)
        self.url = path_dict['url']
        if Config.IMPLEMENTATION == 'flask':
            self.url = self.url.replace('}', '>').replace('{', '<')
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
            if re.match(EXT_REGEX, key):
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


class Content(OpenAPI):
    def __init__(self, _format, content_dict):
        self.format = _format
        self.type = self.get_schema_type(content_dict)

        # TODO
        self.example = content_dict.get('example')
        self.examples = content_dict.get('examples')
        self.encoding = content_dict.get('encoding')
        self.extensions = self.get_extensions(content_dict)


class RequestBody(OpenAPI):
    def __init__(self, dikt):
        request_body_dict = self.get_reference(dikt)

        self.formats = self.get_content_formats(request_body_dict)  # array<string>
        self.types = self.get_content_types(request_body_dict)  # array<string>
        self.contents = self.get_contents(request_body_dict)  # array<Content>

        # TODO
        self.required = self.to_boolean(request_body_dict.get('required'))
        self.description = request_body_dict.get('description')
        self.extensions = self.get_extensions(request_body_dict)


class Response(OpenAPI):
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


class Parameter(OpenAPI):
    def __init__(self, dikt):
        parameter_dict = self.get_reference(dikt)

        self.name = JavaScript.get_name(parameter_dict.get('name'))  # REQUIRED
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


class Model(OpenAPI):
    def __init__(self, name, schema_dict):
        self.name = name
        # key is filename, value is class that is being imported. **NOT SURE IF THIS WILL BE KEPT**
        self.dependencies = self.get_dependencies(schema_dict)
        self.properties = self.get_properties(schema_dict)  # dictionary with key is property name, value is property type
        self.has_enums = self.enums_exist(schema_dict)

    def enums_exist(self, schema_dict):
        for attribute_name, attribute_dict in schema_dict['properties'].items():
            if attribute_dict.get('enum') is not None:
                return True

        return False

    def get_dependencies(self, schema_dict):

        def get_dep_by_attr(attribute_dict):
            deps_by_attr = []

            ref = attribute_dict.get('$ref')
            if ref is not None:
                deps_by_attr.append(ref.split('/')[3])

            elif attribute_dict['type'] == 'array':
                deps_by_attr = deps_by_attr + get_dep_by_attr(attribute_dict['items'])

            return deps_by_attr

        dependencies = []

        for attribute_name, attribute_dict in schema_dict['properties'].items():
            attr_deps = get_dep_by_attr(attribute_dict)
            dependencies = dependencies + attr_deps

        return dependencies

    def get_properties(self, schema_dict):
        if schema_dict.get('properties') is None:
            return []

        properties = []
        for property_name, property_dict in schema_dict['properties'].items():
            properties.append(Property(property_name, property_dict, schema_dict.get('required')))

        return properties


class Property(OpenAPI):
    def __init__(self, name, schema_dict, required_list):  # DOESN'T TAKE INTO CONSIDERATION REFERENCES
        self.name = name
        self.type = self.get_type(schema_dict)
        self.is_required = self.attr_required(name, required_list)
        self.enums = schema_dict.get('enum')

    def attr_required(self, attribute_name, required_list):
        if required_list is None:
            return False
        return attribute_name in required_list
