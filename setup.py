import os.path
from setuptools import setup, find_packages

def get_requirements():
    reqsfile = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(reqsfile, 'r') as fp:
        return [req.strip() for req in fp if req.strip() != '' \
                and not req.strip().startswith('#')]

setup(
    name='ensconce-converters',
    version='0.1',
    description='Converts Ensconce GPG export to Keepass 1.x DB file (KDB).',
    license='GPLv3', # matching license of included keepassdb library. 
    install_requires=get_requirements(),  
    packages = find_packages('.'),
    include_package_data=True,
    package_data={'ensconce_converters': ['templates/*.html']},
    test_suite='nose.collector',
    zip_safe=False,
    entry_points="""
    [console_scripts]
    ensconce2keepass=ensconce_converters.cli:keepass
    """,
)
