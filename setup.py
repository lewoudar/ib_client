from setuptools import find_packages, setup

from infoblox import __version__

setup(
    name='infoblox-client',
    version=__version__,
    author='Kevin Tewouda',
    author_email='lewoudar@gmail.com',
    description='Infoblox client',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'click',
        'pygments'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Terminals',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'ib=infoblox.scripts:cli'
        ],
    },
)
