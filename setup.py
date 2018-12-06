# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['jira_oauth_generator']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=1.7,<2.0',
 'asn1crypto>=0.24.0,<0.25.0',
 'certifi>=2018.11,<2019.0',
 'cffi>=1.11,<2.0',
 'chardet>=3.0,<4.0',
 'click>=7.0,<8.0',
 'cryptography>=2.4,<3.0',
 'defusedxml>=0.5.0,<0.6.0',
 'httplib2>=0.12.0,<0.13.0',
 'idna>=2.8,<3.0',
 'jira>=2.0,<3.0',
 'oauth2>=1.9,<2.0',
 'oauthlib>=2.1,<3.0',
 'pbr>=5.1,<6.0',
 'pycparser>=2.19,<3.0',
 'six>=1.11,<2.0',
 'tlslite>=0.4.9,<0.5.0',
 'urllib3>=1.24,<2.0']

setup_kwargs = {
    'name': 'jira-oauth-generator',
    'version': '0.1.0',
    'description': 'Generator of access token for Jira OAuth',
    'long_description': None,
    'author': 'Raju Kadam',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
