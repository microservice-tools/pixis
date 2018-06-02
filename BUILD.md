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

Pixis uses 3 drivers to execute code generation functions:
- **once_iterator()**
- **schemas_iterator()**
- **tags_iterator()**

TODO...


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

```python
@staticmethod
    def stage_default_iterators():
        utils.stage_iterator(utils.once_iterator, [Flask.generate_once, Flask.generate_custom])
        utils.stage_iterator(utils.tag_iterator, [Flask.generate_per_tag])
        utils.stage_iterator(utils.schema_iterator, [Flask.generate_per_schema])
```




