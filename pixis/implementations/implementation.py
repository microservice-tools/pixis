class Implementation():
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
    def custom_iterator():
        pass

    @staticmethod
    def once_iterator(once_iterator_functions):
        for f in once_iterator_functions:
            f()

    @staticmethod
    def schema_iterator(schema_iterator_functions):
        for schema_name, schema in TEMPLATE_CONTEXT['schemas'].items():
            TEMPLATE_CONTEXT['_current_schema'] = schema_name
            for f in schemas_iterator_functions:
                f()

    @staticmethod
    def tag_iterator(tag_iterator_functions):
        for tag, paths in TEMPLATE_CONTEXT['paths'].items():
            TEMPLATE_CONTEXT['_current_tag'] = tag
            for f in tag_iterator_functions:
                f()

    @staticmethod
    def process():
        pass

    @staticmethod
    def lower_first(s):
        return s[:1].lower() + s[1:] if s else ''
