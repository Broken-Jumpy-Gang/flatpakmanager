from setuptools import setup, find_packages

import configparser
if not hasattr(configparser, 'SafeConfigParser'):
    configparser.SafeConfigParser = configparser.RawConfigParser

setup(
    name="flatpak-manager",
    version="0.1.1",
    description="A tool for managing flatpak applications",
    long_description="A TUI for managing flatpak applications from within a terminal",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'flatpak-manager = flatpakmanager.main:main_cli',
        ],
    },
    install_requires=[
        "pexpect>=4.8.0"
    ],
)
