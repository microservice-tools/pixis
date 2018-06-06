"""
- This module contains classes relevant for representing aspects of the OpenAPI specification
- Processing done in these classes will use swagger data types and unchanged names
- Language translations and implementation requirements will be handled in their respective modules
"""
import re
from collections import OrderedDict

import pixis.config as cfg

EXT_REGEX = re.compile('x-.*')


class OpenAPI():
    """An abstract base class containing common functions for derived classes (such as Path, Response, RequestBody, etc)
    """

    def _get_reference(self, dikt):
        """Resolves the reference, if there was one

        Retrieves the reference from the spec, or just returns @dikt

        Args:
            dikt (dict): The dictionary that we want to resolve the potential reference for

        Returns:
            A dict that is either the reference, or @dikt
        """
        if '$ref' not in dikt:
            return dikt

        ref_path = dikt['ref'].split('/')

        return cfg.Config.SPEC_DICT[ref_path[1]][ref_path[2]][ref_path[3]]

    def _get_extensions(self, dikt):
        """Retrieves all extensions from @dikt

        Args:
            dikt (dict): The dictionary that we want to retrieve the extensions for

        Returns:
            A dict that contains all extensions found in @dikt as key, value pairs.
            If no extensions exist, returns an empty dictionary
        """
        extensions = {}

        for key, value in dikt.items():
            if re.match(EXT_REGEX, key):
                extensions[key] = value

        return extensions

    def _get_contents(self, dikt):
        """Retrieves all Content objects (format and type) from @dikt

        Args:
            dikt (dict): The dictionary that we want to retrieve Contents for

        Returns:
            A list of Content objects sorted by format
        """
        content_dict = dikt.get('content')
        if content_dict is None:
            return []

        contents = []
        for _format, info in content_dict.items():
            contents.append(Content(_format, info))

        return sorted(contents, key=lambda k: k.format)

    def _get_content_formats(self, dikt):
        """Retrieves the formats allowed from @dikt

        Args:
            dikt (dict): The dictionary that we want to retrieve content formats for

        Returns:
            A sorted list of strings that describe accepted formats
        """
        contents = self._get_contents(dikt)
        if contents is None:
            return []

        formats = []
        for content in contents:
            formats.append(content.format)

        return sorted(formats)

    def _get_content_types(self, dikt):
        """Retrieves the format types from @dikt

        Args:
            dikt (dict): The dictionary that we want to retrieve content format types for

        Returns:
            A sorted list of strings that describe accepted format types
        """
        contents = self._get_contents(dikt)
        if contents is None:
            return []

        types = []
        for content in contents:
            types.append(content.type)

        return sorted(types)

    def _get_schema_type(self, dikt):
        """Retrieves the formats allowed from @dikt

        Args:
            dikt (dict): The dictionary that we want to retrieve content formats for

        Returns:
            A list of strings that describe accepted formats
        """
        schema_dict = dikt.get('schema')
        if schema_dict is None:
            return None

        return self._get_type(schema_dict, "")

    def _get_type(self, schema_dict, model_attr_name, depth=0):
        ref = schema_dict.get('$ref')
        if ref is not None:
            s = ref.split('/')[3]
            for _ in range(depth):
                s += cfg.Config.LANGUAGE.to_lang_type('>')
            return s
        if schema_dict.get('type') == 'array':
            return cfg.Config.LANGUAGE.to_lang_type('array') + cfg.Config.LANGUAGE.to_lang_type('<') + self._get_type(schema_dict['items'], model_attr_name, depth + 1)

        if schema_dict.get('type') == 'object':
            s = model_attr_name
        else:
            _format = schema_dict.get('format')
            if _format is not None:
                s = cfg.Config.LANGUAGE.to_lang_type(_format)
            else:
                s = cfg.Config.LANGUAGE.to_lang_type(schema_dict['type'])

        for _ in range(depth):
            s += cfg.Config.LANGUAGE.to_lang_type('>')

        return s

    def _to_boolean(self, s):
        """Helper function to resolve strings and None to boolean values

        Args:
            s (None OR str): What we want to make boolean

        Returns:
            A boolean value. None and non-string values result in False
        """
        if isinstance(s, bool):
            return s
        if isinstance(s, str) and s.lower() == 'true':
            return True
        return False

    def __repr__(self):
        return str(self.__dict__)


class Path(OpenAPI):
    """
    description, summary, servers, parameters, extensions can be from higher level
    paths have references, but not sure if we're going to support it because seems like OpenAPI doesn't support it either?
    highest level extensions aren't supported (i.e. paths -> ^x-)
    """

    def __init__(self, parent_dict, operation_dict):
        path_dict = self._merge_dicts(parent_dict, operation_dict)
        self.url = path_dict['url']
        self.tag = self._get_tag(path_dict)
        self.method = path_dict['method']
        self.function_name = path_dict.get('operationId')
        self.parameters = self._get_parameters(path_dict)  # List[Parameter] ; sorted (required params first, then sorted by name)
        self.parameters_in = self._get_parameters_in()  # List[str] ; sorted and doesn't contain duplicates
        self.request_body = self._get_request_body(path_dict)
        self.responses = self._get_responses(path_dict)  # OrderedDict[str, Response] ; sorted by code
        self.response_formats = self._get_response_formats()  # List[str] ; sorted and doesn't contain duplicates
        self.dependencies = self._get_dependencies(path_dict)  # List[str] ; sorted and doesn't contain duplicates
        self.summary = path_dict.get('summary')
        self.description = path_dict.get('description')
        self.deprecated = self._to_boolean(path_dict.get('deprecated'))
        self.extensions = self._get_extensions(path_dict)

        # TODO
        self.externalDocs = path_dict.get('externalDocs')
        self.callbacks = path_dict.get('callbacks')
        self.security = path_dict.get('security')
        self.servers = path_dict.get('servers')

    def _get_dependencies(self, path_dict):
        """Retrieves the schema classes that the path depends on

        Searches through 'requestBody' and 'responses' inside @path_dict

        Args:
            path_dict (dict): The dictionary that we want to find schemas in

        Returns:
            A set of strings (schema names)
        """
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
                response = self._get_reference(dikt)
                if 'content' in response:
                    for _format, content in response['content'].items():
                        dependencies.add(get_dependency(content))

        request_body_dict = path_dict.get('requestBody')
        if request_body_dict is not None:
            request_body = self._get_reference(request_body_dict)
            for _format, content in request_body['content'].items():
                dependencies.add(get_dependency(content))

        if None in dependencies:
            dependencies.remove(None)

        return sorted(list(dependencies))

    def _get_tag(self, path_dict):
        """Retrieves the first tag from @path_dict

        Args:
            path_dict (dict): The dictionary that we want the tag for

        Returns:
            A str for @path_dict first tag
        """
        tags = path_dict.get('tags')
        if tags is None:
            return None
        return tags[0]

    def _get_response_formats(self):
        """Retrieves the response formats from self.responses

        Returns:
            A set of str describing the accepted response formats
        """
        # self.responses will never be None
        response_formats = set()

        for code, response in self.responses.items():
            for _format in response.formats:
                response_formats.add(_format)

        return sorted(list(response_formats))

    def _get_request_body(self, path_dict):
        """Retrieves the request body from @path_dict

        Args:
            path_dict (dict): The dict that we want the request body for

        Returns:
            A RequestBody object that describes the requestBody from @path_dict
        """
        request_body_dict = path_dict.get('requestBody')
        if request_body_dict is None:
            return None

        return RequestBody(request_body_dict)

    def _get_parameters_in(self):
        """Retrieves all possible parameter input locations for a path

        Returns:
            A set that includes all possible parameter input locations for the path
        """
        if self.parameters is None:
            return set()

        parameters_in = set()
        for parameter in self.parameters:
            parameters_in.add(parameter._in)

        return sorted(list(parameters_in))

    def _get_parameters(self, path_dict):
        """Retrieves all parameters for a path

        Args:
            path_dict (dict): The dict that we want the parameters for

        Returns:
            A list of Parameter objects for a path
        """
        params_list = path_dict.get('parameters')
        if params_list is None:
            return []

        parameters = []
        for param_dict in params_list:
            parameters.append(Parameter(param_dict))

        return sorted(sorted(parameters, key=lambda k: k.name), key=lambda k: k.required)

    def _get_responses(self, path_dict):
        """Retrieves all responses for a path

        Args:
            path_dict (dict): The dict that we want the responses for

        Returns:
            A dict of string to Response objects for a path
        """
        resp_dict = path_dict.get('responses')

        responses = {}
        for code, response_dict in resp_dict.items():
            responses[code] = Response(code, response_dict)

        return OrderedDict(sorted(responses.items()))

    def _merge_dicts(self, fallback_dict, priority_dict):
        """Merges the main parent path dict from the spec into the child path dict

        Prioritizes values from the child path dict @priority_dict

        Args:
            fallback_dict (dict): The parent path dict
            priority_dict (dict): The child path dict

        Returns:
            A dict of strings to all path values
        """
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
                priority_parameter_dict = self._get_reference(item)
                unique_parameters.add((priority_parameter_dict['name'], priority_parameter_dict['in']))

            for item in fallback_parameters:
                fallback_parameter_dict = self._get_reference(item)
                key = (fallback_parameter_dict['name'], fallback_parameter_dict['in'])
                if key not in unique_parameters:
                    dikt['parameters'].append(fallback_parameter_dict)

        return dikt


class Content(OpenAPI):
    def __init__(self, _format, content_dict):
        self.format = _format
        self.type = self._get_schema_type(content_dict)
        self.extensions = self._get_extensions(content_dict)

        # TODO
        self.example = content_dict.get('example')
        self.examples = content_dict.get('examples')
        self.encoding = content_dict.get('encoding')


class RequestBody(OpenAPI):
    def __init__(self, dikt):
        request_body_dict = self._get_reference(dikt)

        self.formats = self._get_content_formats(request_body_dict)  # List[str] ; sorted
        self.types = self._get_content_types(request_body_dict)  # List[str] ; sorted
        self.contents = self._get_contents(request_body_dict)  # List[Content] ; sorted by format
        self.description = request_body_dict.get('description')
        self.extensions = self._get_extensions(request_body_dict)

        # TODO
        self.required = self._to_boolean(request_body_dict.get('required'))


class Response(OpenAPI):
    def __init__(self, response_code, dikt):
        response_dict = self._get_reference(dikt)

        self.code = response_code  # string
        self.formats = self._get_content_formats(response_dict)  # List[str] ; sorted
        self.types = self._get_content_types(response_dict)  # List[str] ; sorted
        self.contents = self._get_contents(response_dict)  # List[Content] ; sorted by format
        self.description = response_dict.get('description')  # REQUIRED
        self.extensions = self._get_extensions(response_dict)

        # TODO
        self.headers = response_dict.get('headers')


class Parameter(OpenAPI):
    def __init__(self, dikt):
        parameter_dict = self._get_reference(dikt)

        self.name = parameter_dict.get('name')  # REQUIRED str
        self._in = parameter_dict.get('in')  # REQUIRED str
        self.required = self._to_boolean(parameter_dict.get('required'))  # bool
        self.type = self._get_schema_type(parameter_dict)  # str TODO
        self.description = parameter_dict.get('description')
        self.deprecated = self._to_boolean(parameter_dict.get('deprecated'))
        self.style = parameter_dict.get('style')
        self.allowEmptyValue = self._to_boolean(parameter_dict.get('allowEmptyValue'))
        self.explode = self._to_boolean(parameter_dict.get('explode'))
        self.allowReserved = self._to_boolean(parameter_dict.get('allowReserved'))
        self.extensions = self._get_extensions(parameter_dict)

        # TODO
        self.example = parameter_dict.get('example')
        self.examples = parameter_dict.get('examples')


# class Schema(OpenAPI):
#     def __init__(self, name, schema_dict):

#         # strict JSON schema properties as defined by https://tools.ietf.org/html/draft-wright-json-schema-validation-00
#         self.title = schema_dict.get('title')  # str
#         self.pattern = schema_dict.get('pattern')  # str ; Should be a valid regular expression. A string instance is valid if the regex matches successfully
#         self.uniqueItems = self._to_boolean(schema_dict.get('uniqueItems'))  # bool ; Defaults to False. If True, instance validates successfully if all elements are unique. If False, instance validates
#         self.exclusiveMaximum = self._to_boolean(schema_dict.get('exclusiveMaximum'))  # bool ; Represents whether the limit in self.maximum is exclusive or not. Defaults to False
#         self.exclusiveMinimum = self._to_boolean(schema_dict.get('exclusiveMinimum'))  # bool ; Represents whether the limit in self.minimum is exclusive or not. Defaults to False
#         self.multipleOf = schema_dict.get('multipleOf')  # number > 0 ; A numeric instance is only valid if division by self.multipleOf results in an integer
#         if self.multipleOf is not None:
#             self.multipleOf = float(self.multipleOf)
#         self.maximum = schema_dict.get('maximum')  # number ; Represents an upper limit for a numberic instance. Validates with self.exclusiveMaximum
#         if self.maximum is not None:
#             self.maximum = float(self.maximum)
#         self.minimum = schema_dict.get('minimum')  # number ; Represents a lower limit for a numberic instance. Validates with self.exclusiveMinimum
#         if self.minimum is not None:
#             self.minimum = float(self.minimum)
#         self.maxLength = schema_dict.get('maxLength')  # int >= 0 ; A string instance is valid if its length is <= self.maxLength
#         if self.maxLength is not None:
#             self.maxLength = int(self.maxLength)
#         self.minLength = schema_dict.get('minLength', 0)  # int <= 0 ; A string instance is valid if its legnth is >= self.minLength
#         if self.minLength != 0:
#             self.minLength = int(self.minLength)
#         self.maxItems = schema_dict.get('maxItems')  # int >= 0 ; An array instance is valid if its size <= self.maxItems
#         if self.maxItems is not None:
#             self.maxItems = int(self.maxItems)
#         self.minItems = schema_dict.get('minitems', 0)  # int <= 0 ; An array instance is valid if its size >= self.minitems
#         if self.minItems != 0:
#             self.minItems = int(self.minItems)
#         self.maxProperties = schema_dict.get('maxProperties')  # int <= 0 ; An array instance is valid if its size >= self.maxProperties
#         if self.maxProperties is not None:
#             self.maxProperties = int(self.maxProperties)
#         self.minProperties = schema_dict.get('minProperties', 0)  # int >= 0 ; An array instance is valid if its size <= self.minProperties
#         if self.minProperties != 0:
#             self.minProperties = int(self.minProperties)
#         # TODO
#         self.required = schema_dict.get('required')  # List[str] ; Must have at least one element, and elements must be unique. Object instance is valid against this keyword if its property set contains all elements in self.required
#         self.enum = schema_dict.get('enum')  # List[any] ; Should have at least one element, and elements should be unique. An instance validates successfully against this keyword if its value is equal to an element in self.enum

#         # modified JSON schema properties defined by https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#schemaObject
#         self.type = schema_dict.get('type')  # str ; value must be one of the primitive types: string number object array boolean null. An instance matches successfully if its type matches
#         self.description = schema_dict.get('description')  # str
#         self.format = schema_dict.get('format')  # str
#         # TODO
#         self.allOf = schema_dict.get('allOf')  # List[Schema OR Reference]
#         self.oneOf = schema_dict.get('oneOf')  # List[Schema OR Reference]
#         self.anyOf = schema_dict.get('anyOf')  # List[Schema OR Reference]
#         self.Not = schema_dict.get('not')  # List[Schema OR Reference]
#         self.items = schema_dict.get('items')  # Schema OR Reference ; must be present if self.type is array
#         self.properties = schema_dict.get('properties')  # Dict[str, Schema OR Reference] ; key is schema name
#         self.default = schema_dict.get('default')  # any ; value must conform to self.type
#         # https://stackoverflow.com/questions/41239913/why-additionalproperties-is-the-way-to-represent-dictionary-map-in-swagger-ope/41240118#41240118
#         # explanation for self.additionalProperties below
#         self.additionalProperties  # bool OR Dict[str, Schema OR Reference]

#         # "the following fields MAY be used for further schema documentation"
#         self.nullable = self._to_boolean(schema_dict.get('nullable'))
#         self.readOnly = self._to_boolean(schema_dict.get('nullable'))
#         self.writeOnly = self._to_boolean(schema_dict.get('writeOnly'))
#         self.deprecated = self._to_boolean(schema_dict.get('deprecated'))
#         self.extensions = self._get_extensions(schema_dict)
#         # TODO
#         self.externalDocs = schema_dict.get('externalDocs')
#         self.example = schema_dict.get('example')
#         self.xml = schema_dict.get('xml')
#         self.discriminator = schema_dict.get('discriminator')

#         """
#         self.properties defines the known set of properties,
#         but if we want to have something like a dict/hashmap where
#         we can't specify how many keys there will be or what they are in advance,
#         that's when we use self.additionalProperties.
#         self.additionalProperties will match any property name (which will be the key),
#         and the $ref/type from self.additionalProperties will be the value.
#         Unique keys is enforced naturally due to hashmap definition

#         If "additionalProperties" is absent, it may be considered present
#         with an empty schema as a value.

#         If "additionalProperties" is true, validation always succeeds.

#         If "additionalProperties" is false, validation succeeds only if the
#         instance is an object and all properties on the instance were covered
#         by "properties" and/or "patternProperties".

#         If "additionalProperties" is an object, validate the value as a
#         schema to all of the properties that weren't validated by
#         "properties" nor "patternProperties".
#         """


class Schema(OpenAPI):
    """
    A class for a schema object defined for the template context
    Attributes follow the OpenAPI v3.0 specification
    """

    def __init__(self, name, schema_dict):
        """
        Assigns name and type attributes of property, whether property is required by its schema object and list of enums for the property

        Args:
            name (str): name of schema object
            schema_dict(Dict): attribute dictionary of schema object

        Attributes:
            name (str): name of schema object
            dependencies (List[str]): dependencies needed by schema object
            has_enums (bool): True if schema object has at least one enum, False otherwise
            title (str): title of schema object
            description (str): description of schema object
            default (str): default value if none is provided
            type (str): type of schema object
                Possible values are 'array', 'boolean', 'integer', 'number', 'object', and 'string'
            format (str): format of the schema object type
                Possible values are: 'int32' and 'int64' if type is 'integer'; 'float' and 'double' if type is 'number'; 'byte', 'binary', 'date', 'date-time' and 'password' if type is 'string';

        """
        self.name = name
        self.dependencies = self.get_dependencies(schema_dict)
        self.has_enums = self.enums_exist(schema_dict)
        self.title = schema_dict.get('title')
        self.description = schema_dict.get('description')
        self.default = schema_dict.get('default')
        self.type = schema_dict.get('type')
        self.format = schema_dict.get('format')

        # if type is object
        # additionalProperties can be schema_object or ref
        self.additionalProperties = self.get_additional_properties(schema_dict.get('additionalProperties'))
        self.maxProperties = schema_dict.get('maxProperties')
        self.minProperties = schema_dict.get('minProperties')
        self.properties = self.get_properties(schema_dict)

        # if type is not specified because schema object is reference to another object
        # creates an empty class
        self.ref = schema_dict.get('$ref')

        # if type is array
        self.maxItems = schema_dict.get('maxItems')
        self.minItems = schema_dict.get('minItems')
        self.uniqueItems = schema_dict.get('uniqueItems')
        # TODO: this is a schema object but does the user need any information from items?
        # a class will only be created for array if the outer schema is an array and it will be an
        # empty class
        # self.items =

        # if type is string
        self.pattern = schema_dict.get('pattern')
        self.maxLength = schema_dict.get('maxLength')
        self.minLength = schema_dict.get('minLength')

        # if type is integer or number
        self.maximum = schema_dict.get('maximum')
        self.exclusiveMaximum = schema_dict.get('exclusiveMaximum')
        self.minimum = schema_dict.get('minimum')
        self.exclusiveMinimum = schema_dict.get('exclusiveMinimum')
        self.multipleOf = schema_dict.get('multipleOf')

    # def snake_to_camel_case(self,name):
    #     return name.title().replace("_","")

    def enums_exist(self, schema_dict):
        """
        Determines if enums exist for schema object

        Args:
            schema_dict (Dict): attribute dictionary of schema object

        Returns:
            True if enums exist for schema object, False otherwise; if properties is not defined, return None
        """
        if schema_dict.get('properties') is not None:
            for attribute_name, attribute_dict in schema_dict['properties'].items():
                if attribute_dict.get('enum') is not None:
                    return True
            return False
        return None  # this can just be False?

    def get_additional_properties(self, schema_dict):
        """
        Gets additional properties of schema object

        Args:
            schema_dict (Dict): 'additionalProperties' attribute dictionary of schema object

        Returns:
            type of additional object if it exists, None otherwise
        """
        if schema_dict is None:
            return None
        else:
            return self._get_type(schema_dict, '')

    def get_dependencies(self, schema_dict):
        """
        Gets dependencies based on 'additionalProperties', references, and 'properties' defined for schema object

        Args:
            schema_dict (Dict): attribute dictionary of schema object

        Returns:
            list of dependencies of schema object
        """
        def get_dep_by_attr(attribute_dict):
            """
            Gets dependencies by each property in schema object by looking at all '$ref' values defined recursively

            Args:
                attribute_dict (Dict): property attributes dictionary

            Returns:
                list of dependencies for that property
            """
            deps_by_attr = []

            ref = attribute_dict.get('$ref')
            if ref is not None:
                deps_by_attr.append(ref.split('/')[3])

            elif attribute_dict.get('type') == 'array':
                deps_by_attr = deps_by_attr + get_dep_by_attr(attribute_dict['items'])

            return deps_by_attr

        dependencies = []

        ref = schema_dict.get('$ref')
        # TODO? flake8 error: assigned to but never used
        # additionalProperties = schema_dict.get('additionalProperties')
        properties = schema_dict.get('properties')

        if ref is not None:
            dependencies.append(ref.split('/')[3])
            return dependencies

        if properties is not None:
            for attribute_name, attribute_dict in schema_dict['properties'].items():
                attr_deps = get_dep_by_attr(attribute_dict)
                dependencies = dependencies + attr_deps

        # TODO: additionalProperties is a schema_obj
        # add refs to dependencies
        # if additionalProperties is not None:
        #      for type in schema_dict['additionalProperties'].items():
        #         attr_deps = get_dep_by_attr(attribute_dict)
        #         dependencies = dependencies + attr_deps

        return dependencies

    def get_properties(self, schema_dict):
        """
        Gets the properties of the object and creates a Property object for each property of the schema object

        Args:
            schema_dict (Dict): properties attributes dictionary of schema object

        Returns:
            list of Property objects
        """
        if schema_dict.get('properties') is None:
            return []

        properties = []
        for property_name, property_dict in schema_dict['properties'].items():
            properties.append(Property(self.name, property_name, property_dict, schema_dict.get('required')))

        return properties


class Property(OpenAPI):
    """
    A class for a property object defined for the template context
    Attributes follow the OpenAPI v3.0 specification
    """

    def __init__(self, schema_name, property_name, schema_dict, required_list):  # DOESN'T TAKE INTO CONSIDERATION REFERENCES
        """
        Assigns name and type attributes of property, whether property is required by its schema object and list of enums for the property

        Args:
            schema_name (str): name for the defined schema the new property object belongs to
            property_name (str): name attribute for property object
            schema_dict (dict): value attributes of property defined from specification file
            required_list (List[str]): list of all required properties of schema object this property belongs to

        Attributes:
            name (str): name of property
            type (str): type of property
                Can be 'string', 'array', 'integer', or 'object'
            is_required (bool): False for not required property of schema object, True for required
            enums (List[str]): possible enums of property
        """
        self.name = property_name
        self.type = self._get_type(schema_dict, schema_name + property_name)
        self.is_required = self.attr_required(property_name, required_list)
        self.enums = schema_dict.get('enum')

    def attr_required(self, attribute_name, required_list):
        """
        Determines if the attribute is required in the schema object

        Args:
            attribute_name (str): name of property to search for in 'required_list'
            required_list (List[str]): list of required names of required properties of schema object

        Returns:
            True if attribute is required in schema object, False otherwise
        """
        if required_list is None:
            return False
        return attribute_name in required_list
