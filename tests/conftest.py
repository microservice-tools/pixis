import pytest
import os
import sys


@pytest.fixture(scope="module")
def serverFiles():
    return gen('build','flask_build.py','swagger.yaml')


@pytest.fixture(scope="module")
def clientFiles():
    return gen('services', 'ang_build.py', 'swagger.yaml')

class gen():
    
    def __init__(self, project_name, build, spec):
        self.name = project_name
        self.build_file = build
        self.yaml_file = spec

        try:
            if os.path.split(os.getcwd())[1] == 'pixis':
                os.chdir('tests')
        except:
            assert 0
        assert os.system('pixis -b ' + self.build_file) == 0
            
    def __del__(self):
        assert os.system('rm -rf ' + self.name + ' && rm Dockerfile')
