import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, "__init__.py")) as f:
        return re.search("__version__ = ['\"]([^'\"]+)['\"]", f.read()).group(1)


def get_long_description():
    """
    Return the README.
    """
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name='ib-client',
    python_requires='>=3.6',
    url='https://bitbucket.org/lewoudar/infoblox_client',
    version=get_version('infoblox'),
    author='Kevin Tewouda',
    author_email='lewoudar@gmail.com',
    description='Infoblox client',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    packages=['infoblox'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'click',
        'pygments',
        'python-dotenv',
        'click-didyoumean',
        'click-completion'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Terminals',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'ib=infoblox.scripts:cli'
        ],
    },
)
