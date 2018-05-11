from setuptools import setup

setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
    version='0.1dev',
    packages=['pixis', ],
    license='MIT',
    include_package_data=True,
    package_data={
        'pixis': ['templates/server_flask/*', 'templates/client_angular2/*'],
    },
    entry_points={
        'console_scripts': [
            'pixis=pixis.main:main',
        ],
    },

)
