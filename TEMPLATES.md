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

Users can modify the template context TODO