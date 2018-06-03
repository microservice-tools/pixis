# **Build file**: Generation Options and Custom Behavior


## Build file variables

| VARIABLE       | TYPE            | DESCRIPTION                                                                                                               | DEFAULT        |
|----------------|-----------------|---------------------------------------------------------------------------------------------------------------------------|----------------|
| SPEC           | string          | Relative filepath to specification file (json/yaml)                                                                       | "swagger.yaml" |
| TEMPLATES      | string          | Relative filepath to local custom templates directory                                                                     | "templates"    |
| OUTPUT         | string          | Relative filepath to desired output                                                                                       | "build"        |
| IMPLEMENTATION | string OR class | One of {'flask', 'angular2} OR a user-defined class                                                                       | "flask"        |
| OVERWRITE      | boolean         | Allows Pixis to overwrite any files during generation                                                                     | False          |
| PROTECTED      | list[string]    | A list of regular expressions as strings describing files that Pixis should never overwrite (unless OVERWRITE is enabled) | []   
---

## Custom code generation

### Important functions:

#### **emit_template(template_path: str, output_dir: str, output_name: str)**
#### **generate_once()**
#### **generate_per_tag()**
#### **generate_per_schema()**
#### **generate_custom()**
#### **once_iterator()**
#### **schema_iterator()**
#### **tag_iterator()**

At the lowest level, *emit_template()* renders a template and outputs the file. This function should be called once for each file that should be generated. All of these *emit_template()* calls should be placed inside the appropriate *generate_x()* function, which is then called by its appropriate *x_iterator()* function.

- *emit_template()* makes the association between which template to use, where to output it, and what it's name should be
- *generate_x()* organizes all of the *emit_template()* calls
- *x_iterator()* actually calls each function a certain number of times

### Generation Control

To make Pixis not generate your model classes, put this inside your build file
```python
import pixis.utils as utils

utils.stage_iterator(utils.schema_iterator, [])
```
The empty brackets mean that the schema_iterator should not call any generation functions

To make Pixis instead use generation functions that you define, put this inside your build file
```python
import pixis.utils as utils

def my_generation_function():
    utils.emit_template('my_template', 'path/to/output/dir', 'my_file.ts')

utils.stage_iterator(utils.schema_iterator, [my_generation_function])
```
---

## Adding new language support

Users must define a class that derives from Pixis' base **Implementation** class

If Pixis does not have a predefined language class for your implementation,
then the user must also define a class that derives from Pixis' base **Language** class

To use these base classes and other needed functions in your build file, import from Pixis like this:
```python
import pixis.utils as utils
from pixis.config import Config
from pixis.implementations.implementation import Implementation
from pixis.languages.language import Language
from pixis.template_handler import TEMPLATE_CONTEXT, emit_template
```

---

### **Language class**

```python
class Language():
    @staticmethod
    def to_lang_type(string):
        return string

    @staticmethod
    def to_lang_style(string):
        return string

    @staticmethod
    def to_camel_case(string):
        # Does stuff
        return new_string

    @staticmethod
    def to_snake_case(string):
        # Does stuff
        return new_string
```

A user-defined Language class should inherit from this base class and override the **to_lang_type()** and **to_lang_style()** functions. These functions are used to provide accurate typing and styling (snake_case or camelCase) for the generated code.

---

### **Implementation class**

```python
class Implementation():
    @staticmethod
    def process():
        pass

    @staticmethod
    def generate_custom():
        pass

    @staticmethod
    def generate_once():
        pass

    @staticmethod
    def generate_per_schema():
        pass

    @staticmethod
    def generate_per_tag():
        pass

    @staticmethod
    def stage_default_iterators():
        raise NotImplementedError()

    @staticmethod
    def lower_first(s):
        return s[:1].lower() + s[1:] if s else ''
```
### **emit_template(template_path: str, output_dir: str, output_name: str)**

This function establishes the relationship between the template to use, where to output, and the resulting filename. Should be placed inside the **generate_x()** functions

### **generate_once()**

This function contains **emit_template()** calls that will only be called once. Files such as *requirements.txt*, *README.md*, encoders, deserializers, base models, and main project files don't need to be generated multiple times.

### **generate_per_schema()**

This function contains **emit_template()** calls that will be called once per schema. It's common for each model to have its own file.

### **generate_per_tag()**

This function contains **emit_template()** calls that will be called once per tag. It's unnecessary to place each path function in its own file, but users will likely want functions that use the same tag or path to be placed together.

### **generate_custom()** 

This function would call **emit_templates()** however many times, or based on any criteria the user wants.

### **process()**

Allow the user to make changes to the template context so that Pixis can accomodate any implementation-specific nuances. For example, path urls that contain parameters wrap the parameters with `{ }` brackets, but Flask requires these path url parameters to be wrapped with `< >` brackets, so this function will make that change.

### **stage_default_iterators()**

Defines the default generation behavior for this implementation

Example:
```python
@staticmethod
    def stage_default_iterators():
        utils.stage_iterator(utils.once_iterator, [Flask.generate_once, Flask.generate_custom])
        utils.stage_iterator(utils.tag_iterator, [Flask.generate_per_tag])
        utils.stage_iterator(utils.schema_iterator, [Flask.generate_per_schema])
```

---

### Build file containing a full custom Flask implementation

```python
import pixis.utils as utils
from pixis.config import Config
from pixis.implementations.implementation import Implementation
from pixis.languages.language import Language
from pixis.template_handler import TEMPLATE_CONTEXT, emit_template

SPEC = 'swagger.yaml'
OUTPUT = 'my_server'
FLASK_SERVER_NAME = 'my_flask_server'


class Python(Language):
    TYPE_MAP = {
        'integer': 'int',
        'int32': 'int',
        'long': 'int',
        'int64': 'int',
        'float': 'float',
        'double': 'float',
        'string': 'str',
        'byte': 'str',
        'binary': 'str',
        'boolean': 'bool',
        'date': 'date',
        'date-time': 'datetime',
        'password': 'str',
        'object': 'object',
        'array': 'List',
        '<': '[',
        '>': ']',
    }

    @staticmethod
    def to_lang_type(string):
        try:
            return Python.TYPE_MAP[string]
        except KeyError as err:
            raise KeyError(err)

    @staticmethod
    def to_lang_style(string):
        return Language.to_snake_case(string)


class Flask(Implementation):
    LANGUAGE = Python

    @staticmethod
    def process():
        for tag, paths in TEMPLATE_CONTEXT['paths'].items():
            for path in paths:
                path.url = path.url.replace('}', '>').replace('{', '<')

    @staticmethod
    def generate_once():
        emit_template('requirements.j2', Config.OUTPUT, 'requirements.txt')
        emit_template('Dockerfile.j2', Config.OUTPUT, 'Dockerfile')
        emit_template('util.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, 'util.py')
        emit_template('encoder.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, 'encoder.py')
        emit_template('base_model.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/models', 'base_model.py')
        emit_template('init.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, '__init__.py')
        emit_template('init.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/models', '__init__.py')
        emit_template('init.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/controllers', '__init__.py')
        emit_template('main.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME, '__main__.py')
        emit_template('setup.j2', Config.OUTPUT, 'setup.py')

    @staticmethod
    def generate_per_tag():
        emit_template('controller.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/controllers', TEMPLATE_CONTEXT['_current_tag'] + '_controller.py')

    @staticmethod
    def generate_per_schema():
        emit_template('model.j2', Config.OUTPUT + '/' + Config.FLASK_SERVER_NAME + '/models', Implementation.lower_first(TEMPLATE_CONTEXT['_current_schema']) + '.py')

    @staticmethod
    def stage_default_iterators():
        utils.stage_iterator(utils.once_iterator, [Flask.generate_once])
        utils.stage_iterator(utils.tag_iterator, [Flask.generate_per_tag])
        utils.stage_iterator(utils.schema_iterator, [Flask.generate_per_schema])


IMPLEMENTATION = Flask
```


