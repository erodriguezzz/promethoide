from setuptools import setup, find_packages

setup(
    name='pycron',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'pycron = pycron.scheduler:main',
        ],
    },
)
