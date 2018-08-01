import setuptools

setuptools.setup(
    version='0.1dev',
    license='MIT',
    packages=setuptools.find_packages(),
    package_data={
        'pixis': ['templates/*'],
        'samples': ['*'],
    },
    entry_points={
        'console_scripts': [
            'pixis=pixis.main:main',
        ],
    },
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    pbr=True,
)
