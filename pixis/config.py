import difflib
import hashlib
import pathlib
from collections import OrderedDict

import jinja2


class Config():
    """Provides variables that pixis uses to configure code generation

    Attributes:
        BUILD: A string that describes relative path to build file
        SPEC: A string that describes relative path to specification file
        TEMPLATES: A string that describes relative path to templates directory
        OUTPUT: A string that describes relative path to output directory
        PARENT: A string that describes relative path to output directory's parent directory (Determined from OUTPUT)
        FLASK_SERVER_NAME: A string that describes the directory name for default Flask server implementation
        VERBOSE: A boolean for Verbose mode (TODO)
        OVERWRITE: A boolean for Force Overwrite
        PROTECTED: A list of strings that describe file names or regular expressions for files that Pixis should never overwrite (even if OVERWRITE is True)
        LANGUAGE: A subclass of Language (Defined from IMPLEMENTATION)
        IMPLEMENTATION: A string that describes a supported implementation {'flask', 'angular2'} OR a subclass of Implementation
        SPEC_DICT: raw specification dictionary
        _checksums: Internal Pixis map for current file checksums
    """
    # DEFAULTS
    # These are relative paths
    BUILD = 'build.py'
    SPEC = 'swagger.yaml'
    TEMPLATES = 'templates'
    OUTPUT = 'build'
    PARENT = None

    FLASK_SERVER_NAME = 'flask_server'
    VERBOSE = False
    OVERWRITE = False
    PROTECTED = []

    LANGUAGE = None
    IMPLEMENTATION = 'flask'

    SPEC_DICT = {}
    _iterators_mapping = OrderedDict()
    _iterator_functions_mapping = OrderedDict()
    _checksums = {}


class Language():
    """
    Language - base abstract class; provides default methods for specific language classes to override
    """
    @staticmethod
    def to_lang_type(string):
        return string

    @staticmethod
    def to_lang_style(string):
        return string

    @staticmethod
    def to_camel_case(string):
        s = string[0].lower()
        capitalize = False
        for char in string[1:-1]:
            if char == '_':
                capitalize = True
            else:
                if capitalize:
                    s += char.upper()
                else:
                    s += char
                capitalize = False
        return s + string[-1]

    @staticmethod
    def to_snake_case(string):
        s = string[0].lower()
        for char in string[1:-1]:
            if char.isupper():
                s += '_' + char.lower()
            else:
                s += char
        return s + string[-1].lower()


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


def stage_iterator(x_iterator, x_iterator_functions):
    """Stages iterators and their functions to be executed

    Args:
        x_iterator (function): iterator function to execute. Defaults are: *once_iterator()*, *schema_iterator()*, *tag_iterator()*
        x_iterator_functions (List[function]): list of functions to be executed by specified iterator
    """
    iterator_name = x_iterator.__name__
    Config._iterators_mapping[iterator_name] = x_iterator
    Config._iterator_functions_mapping[iterator_name] = [f for f in x_iterator_functions]


def once_iterator(once_iterator_functions):
    """Executes each function in @once_iterator_functions once

    Args:
        once_iterator_functions (List[function]): functions that this iterator will execute
    """
    for f in once_iterator_functions:
        f()


def schema_iterator(schema_iterator_functions):
    """Executes each function in @schema_iterator_functions once per schema

    Args:
        schema_iterator_functions (List[function]): functions that this iterator will execute
    """
    import pixis.template_handler as tmpl
    for schema_name, schema in tmpl.TEMPLATE_CONTEXT['schemas'].items():
        tmpl.TEMPLATE_CONTEXT['_current_schema'] = schema_name
        for f in schema_iterator_functions:
            f()


def tag_iterator(tag_iterator_functions):
    """Executes each function in @tag_iterator_functions once per tag

    Args:
        tag_iterator_functions (List[function]): functions that this iterator will execute
    """
    import pixis.template_handler as tmpl
    for tag, paths in tmpl.TEMPLATE_CONTEXT['paths'].items():
        tmpl.TEMPLATE_CONTEXT['_current_tag'] = tag
        for f in tag_iterator_functions:
            f()


def emit_template(template_path: str, output_dir: str, output_name: str) -> None:
    import pixis.template_handler as tmpl
    """Creates a file using template defined by @template_path into directory defined by @output_dir with filename defined by @output_name

    Args:
        template_path (str): where the template is and what the template file's name is
        output_dir (str): where to output files
        output_name (str): name of output file name
    """
    file_path = pathlib.Path(output_dir) / pathlib.Path(output_name)

    try:  # check for their custom templates
        template_name = pathlib.Path(template_path).name
        template_loader = jinja2.FileSystemLoader(Config.TEMPLATES)
        env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
        template = env.get_template(template_name)  # template_path is something like: server_flask/model.j2, so we have to do a name comparison here
        print("Generated file [" + str(file_path) + "] from user-defined template")
    except jinja2.exceptions.TemplateNotFound:
        try:  # check for template in Pixis
            template_loader = jinja2.PackageLoader('pixis', 'templates')
            env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True, line_comment_prefix='//*')
            template = env.get_template(template_path)
        except jinja2.exceptions.TemplateNotFound as err:
            raise ValueError('Template does not exist\n')

    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)  # make directories if it does not already exist
    new_file_text = template.render(tmpl.TEMPLATE_CONTEXT)
    new_file_checksum = hashlib.md5(new_file_text.encode('utf-8')).hexdigest()

    def is_protected(file_path):
        # PosixPath('build/server/hello.py') -> PosixPath('/server/hello.py')
        p = pathlib.Path(str(pathlib.Path('/')) + str(file_path.relative_to(*file_path.parts[:1])))
        for s in Config.PROTECTED:
            if s in str(p):
                return True
            try:
                pattern = re.compile(s)
                if pattern.match(str(p)):
                    return True
            except re.error:
                pass

        return False

    def maybe_generate(file_path, cur_file_text, new_file_text, new_file_checksum):
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
        Config._checksums[str(path)] = checksum

    if is_protected(file_path):
        print("Did not generate [" + str(file_path) + "] (PROTECTED)")
        return

    if Config.OVERWRITE:
        generate_file(file_path, new_file_text, new_file_checksum)
        print("Generated [" + str(file_path) + "] (OVERWRITE flag set and not PROTECTED)")
        return

    old_file_checksum = Config._checksums.get(str(file_path))
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
        maybe_generate(file_path, cur_file_text, new_file_text, new_file_checksum)
        return

    if new_file_checksum == old_file_checksum:
        print('Did not generate [' + str(file_path) + '] (would generate same file as last time)')
        return

    if cur_file_checksum == old_file_checksum:
        generate_file(file_path, new_file_text, new_file_checksum)
        print("Generated [" + str(file_path) + "]. File is unmodified, but something has changed (templates/Pixis/etc)")
        return

    maybe_generate(file_path, cur_file_text, new_file_text, new_file_checksum)
