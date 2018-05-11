from pixis.languages.language import Language
from pixis.implementations.implementation import Implementation

SPEC = 'swagger.yaml'
IMPLEMENTATION = MyImplementation
OUT = 'build'


class MyImplementation(Implementation):
    LANGUAGE = MyLanguage


class MyLanguage(Language):
    pass
