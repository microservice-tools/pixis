# Creating Custom Templates

In order to simplify template creation, Pixis provides the user with a **template context** that represents everything in the specification while making the variables easier to access



## Template Context
* Object/dictionary/list access uses Python syntax

These variables can be used by templates:

---

### **schemas**
* Dictionary from string to Schema Object
* Keys are the names of the schemas

Example:
```
# Defined like:
schemas = {
    schema1_name: schema1,
    schema2_name: schema2,
}

# Use in template like:
{% for prop in schemas[current_schema].properties %}
    {{prop.name}}
{% endfor %}
```

Schema Object Attributes (ex. schema1.name)
---
| VARIABLE       | TYPE            | DESCRIPTION                                                                    |
|---------------------|-------------------|------------------------------------------------------------------------------|
| name               | string             | name of schema object                                                       |
| dependencies  | List[str]          | type of property object                         |
| has_enums      | bool               | True if schema object has at least one enum, False otherwise |
| title                   | string             | title of schema object                                                         |
| description       | string             | description of schema object                                              |
| default              | string            |  default value if one is provided                                           |
| type                  | string            | type of schema object. Possible values are 'array', 'boolean', 'integer', 'number', 'object', and 'string' |
| format               | string            |  format of the schema object type. Possible values are: 'int32' and 'int64' if type is 'integer'; 'float' and 'double' if type is 'number'; 'byte', 'binary', 'date', 'date-time' and 'password' if type is 'string';  |
|additionalProperties| schema_object or ref | This contains an list of schema objects  | 
|maxProperties| integer | An object instance is valid against "maxProperties" if its number of properties is less than, or equal to, the value of this keyword | 
|minProperties| integer | An object instance is valid against "minProperties" if its number of properties is greater than, or equal to, the value of this keyword. | 
|properties| List[Property] | Contains a list of properties that the objects will have. The property is a class that we have created that contains the name, type, whether or not it is required, and enums if it has any. | 
|ref| string | reference to a schema within the components section | 
|maxItems| number | Minimum count of items in array | 
|minItems| number | Minimum count of items in array | 
|uniqueItems| boolean | Allow only unique items in array |
|pattern| string | This string SHOULD be a valid regular expression | 
|maxLength| integer | Maximum string's length | 
|minLength| integer | Minimum string's length |
|maximum| number | Maximum value |
|exclusiveMaximum| boolean | Indicate if the value must value < maximum |
|minimum| number | Maximum value |
|exclusiveMinimum| boolean | Indicate if the value must value > minimum |
|multipleOf| number | The value must be a multiple of multiplOf |
### **Property**
A class for a property object defined for the template context. The Attributes follow the OpenAPI v3.0 specification.

| VARIABLE       | TYPE            | DESCRIPTION                                                                    |
|---------------------|-------------------|------------------------------------------------------------------------------|
| name               | string             | name of property                                                       |
| type                 | string             | dependencies required by schema object  (integer, number, boolean, or string)                          |
| is_required      | bool               | False for not required property of schema object, True for required |
| enums             | List[str]           | possible enums of property. If no enums it is an empty list.|


---

### **paths**
* Dictionary from string to list of Path Objects
* Keys are the tags for the API
* Values are all of the Path Objects with a tag that matches the key
* There are no duplicate Path Objects in the dictionary (same Path Objects would have the same url and method (GET, POST, etc))

*Defined like:*
```python
paths = {
    "tag1": [
        tag1_path1,
        tag1_path2
    ],
    "tag2": [
        tag2_path1,
        tag2_path2,
        tag2_path3,
    ]
}
```
*Use in template like:*
```
{% for path in paths[current_tag] %}
@{{ current_tag }}_api.route('{{path.url}}', methods=['{{path.method}}'])
def {{path.function_name}}({% for param in path.parameters %}{{param.name}}{% if not loop.last %}, {% endif %}{% endfor %}):
    return '{{ path.url }} {{ path.method.upper() }}'
{% endfor %}
```

---

### **cfg**
* Config Class for this API
* All variables defined inside user's build file become an attribute of this class
    * Ex. If you define `my_variable = 15` inside the build file, then `Config.my_variable == 15`, and inside the template, you can do this: `{{ cfg.my_variable }}`

*Defined like:*
```python
class Config():
    BUILD = 'build.py'
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUTPUT = 'build'
    PARENT = None

    FLASK_SERVER_NAME = 'flask_server'
    VERBOSE = False

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    SPEC_DICT = {}
```
*Use in template like:*
```
{{ cfg.FLASK_SERVER_NAME }}
```

---

### **base_path**
* A string describing the base path for this API

*Defined like:*
```python
base_path = "http://localhost"
```
*Use in template like:*
```
{{ base_path }}
```

---

Currently, users can modify/update the template context via the implementation class function **process()**. There will also be a function that can be called straight from the build file as the final step in modifying/updating the template context

Example: In a user's custom Flask implementation, they can override **process()** to make desired changes to the template context to make the Python-Flask code work once generated
```python
class Flask(Implementation):
    LANGUAGE = Python

    @staticmethod
    def process():
        for tag, paths in TEMPLATE_CONTEXT['paths'].items():
            for path in paths:
                path.url = path.url.replace('}', '>').replace('{', '<')
```
