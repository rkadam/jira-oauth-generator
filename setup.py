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
 'requests-oauthlib>=1.0.0,<2.0.0',
 'requests-toolbelt>=0.8.0,<0.9.0',
 'requests>=2.15.1,<3.0.0',
 'six>=1.11,<2.0',
 'tlslite>=0.4.9,<0.5.0',
 'urllib3>=1.24,<2.0']

setup_kwargs = {
    'name': 'jira-oauth-generator',
    'version': '0.1.5',
    'description': 'Generator of access token for Jira OAuth',
    'long_description': "JIRA OAuth1 Setup and Usage\n====================\n\n### Python 3 Setup\n* Create Python 3 Virtual Environment\n```\nmkvirtualenv -p python3 jira_oauth1_py3_env\n```\n* Activate this environment to work on\n```\nworkon jira_oauth1_py3_env\n```\n* Install all required libraries\n```\npip install -r requirements.txt\n```\n\n### RSA Private and Public Key creations\n* Make sure you have **.oauthconfig** folder exists in your home directory\n* Create RSA Private key and store it in file **oauth.pem**\n```\nopenssl genrsa -out oauth.pem 1024\n```\n* Create RSA Public Key and store it in file **oauth.pub**\n```\nopenssl rsa -in oauth.pem -pubout -out oauth.pub\n```\n* Again make sure both files are *copied* to **.oauthconfig** folder in your home directory.\n* Also share RSA Public Key **oauth.pub** with your Jira Admin, as they need it during _Jira Application Link_ creation.\n\n\n### Jira Application Link Creation Steps\n* Logon as a Jira Administrator\n* Go to **Application links** section under **Application** area\n* Enter dummy url (as oauth token used for API access and not web access) *https://jira-oauth1-rest-api-access*\n* Click on **Create new link** button\n* Click **Continue** on next screen\n* Enter something like **Jira OAuth1 REST API access** as a *Application Name*\n* Don't need to fill any other information. Click on **Continue**\n* Now you should able to see new Application link with name **Jira OAuth1 REST API access** created and available under section *Configure Application Links* section\n* Click on *pencil* icon to configure **Incoming Authentication**\n  * Enter **jira-oauth1-rest-api-access** (or any other appropriate string) as *Consumer Key*\n  * Enter same string **jira-oauth1-rest-api-access** (or any other appropriate string) as *Consumer Name*\n  * Enter content of RSA Public key (stored in file **oauth.pub**) as **Public Key**\n  * Click on **Save**\n\n### Prepare for OAuth Dance\nCreate **starter_oauth.config** in **~/.oauthconfig** folder:\n```ini\n[oauth_config]\njira_base_url=https://jira.example.com\nconsumer_key=jira-oauth1-rest-api-access\ntest_jira_issue=EXJIRA-123\n```\n\nPerform Jira OAuth Dance\n================\n* Make sure you are in base directory of this Repo\n* Python Virtual Environment that we create earlier is active.\n* Run **jira_oauth_token_generator.py**\n```\n(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/jira_oauth_token_generator.py\n```\n* Authenticate in browser as directed below and then click **y** for question *Have you authorized me?*\n* After successful oAuth generation, you will get another set of values for **oauth_token** and **oauth_token_secret**. These are you tokens that you need to use access Jira without passing credentials.\n```\n(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/jira_oauth_token_generator.py\nRequest Token: oauth_token=6AOSSREyS9HaACqEcHjcD6RJVms2NjEr, oauth_token_secret=gnpJMfbgUyG8W4dKzFW4PKFbGttV2CWm\n\nGo to the following link in your browser: https://jira.example.com/plugins/servlet/oauth/authorize?oauth_token=6AOSSREyS9HaACqEcHjcD6RJVms2NjEr\nHave you authorized me? (y/n) y\n\nAccess Token: oauth_token=lmOh7LEdvZ2yxKIm5rdQY2ZfZqNdvUV4, oauth_token_secret=gnpJMfbgUyG8W4dKzFW4PKFbGttV2CWm\nYou may now access protected resources using the access tokens above.\n\nAccessing IDEV-1 using generated OAuth tokens:\nSuccess!\nIssue key: IDEV-1, Summary: Internal Devepment Issue #1\n```\n\n## Copy both oauth_token and oauth_token_secret to .oauth_jira_config.<jira_env> file.\n```\n(jira_oauth1_py3_env) ➜  .oauthconfig cat .oauth_jira_config.dev\n[oauth_token_config]\noauth_token=sdfPxIsdfsdfs$sdf234sdgssd$sresdf\noauth_token_secret=rswfsdfsdfjsdjlksjdfljsdlkfjsldfj\nconsumer_key=jira-export-rest-api-access\nuser_private_key_file_name=oauth.pem\n\n[server_info]\njira_base_url=https://jira-dev.teslamotors.com\n\n[jira_oauth_generator]\ntest_issue_key=ITDOS-145\n```\n\n### Using OAuth1 tokens in Sample Jira Script.\n* Using Python Requests library\n```\n(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/access_using_requests_package.py dev\n(EXJIRA) Excitement for JIRA Project People\n(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗\n```\n* Using Python JIRA library\n```\n(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/access_using_jira_library.py prod\nReteriving Issue: ITEST-145\nIssue:ITEST-145, Summary: Test access request\nReteriving 1st three Jira Projects available to you:\nFirst 3 Projects are ['TES', 'TEst', 'TEST']\n```\n\n>Original implementation is available here:\n>\n> https://bitbucket.org/atlassian_tutorial/atlassian-oauth-examples under python/app.py\n",
    'author': 'Raju Kadam',
    'author_email': None,
    'url': 'https://github.com/rominf/jira-oauth-generator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
