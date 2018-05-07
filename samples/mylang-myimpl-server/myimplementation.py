from pixis.implementations.implementation import Implementation
from pixis.config import Config
from mylanguage import MyLanguage


class MyImplementation(Implementation):
    @staticmethod
    def init():
        Config.LANGUAGE = MyLanguage
