"""
* Original implementation is available here: https://bitbucket.org/atlassian_tutorial/atlassian-oauth-examples under python/app.py
* Copied here as jira_oauth_token_generator.py with modifications:
    * Since we are not able to resolve SSL Certification problem, let's disable ssl certificate validation for each REST api call. 
	  client.disable_ssl_certificate_validation = True
	* Strangely first time (before you approve request in browser) when you access data_url, browser returns 200 response with content of zero bytes instead of 401 response as original code says. Hence I've commented out response code validation for this part.
	* Also I've refactored and removed SignatureMethod_RSA_SHA1 into it's own file. This way we can import it into any other python program!
* Python 3 compatible!

* Pre-Requisities:
    * You have generated RSA Private and Public keys and stored them into files "oauth.pem" and "oauth.pub" respectively.
    * config/ directory contain "starter_oauth.config" file with following details:
        jira_base_url=<JIRA Application URL>
        consumer_key=<enter as registered by your Jira Admin during Application Link creation>
    *
"""
from configparser import ConfigParser
from pathlib import Path
from urllib import parse
import base64
import json

from tlslite.utils import keyfactory
import oauth2 as oauth


oauth_config_dir_path = Path.home() / '.oauthconfig'
starter_oauth_config_file = oauth_config_dir_path / 'starter_oauth.config'
rsa_private_key_file_path = oauth_config_dir_path / 'oauth.pem'
rsa_public_key_file_path = oauth_config_dir_path / 'oauth.pub'


# noinspection PyShadowingNames
def get_access_token_url(base_url):
    return base_url + '/plugins/servlet/oauth/access-token'


# noinspection PyShadowingNames
def get_data_url(base_url, test_jira_issue):
    return base_url + f'/rest/api/2/issue/{test_jira_issue}?fields=summary'


def read_rsa_private_key(path):
    with open(file=path, mode='r') as f:
        return f.read()


def read_rsa_public_key(path):
    with open(file=path, mode='r') as key_cert_file:
        return key_cert_file.read()


# noinspection PyPep8Naming
class SignatureMethod_RSA_SHA1(oauth.SignatureMethod):
    name = 'RSA-SHA1'

    # noinspection PyShadowingNames
    def __init__(self, rsa_private_key):
        self.rsa_private_key = rsa_private_key.strip()

    # noinspection PyShadowingNames
    def signing_base(self, request, consumer, token):
        if not hasattr(request,
                       'normalized_url') or request.normalized_url is None:
            raise ValueError("Base URL for request is not set.")

        sig = (
            oauth.escape(request.method),
            oauth.escape(request.normalized_url),
            oauth.escape(request.get_normalized_parameters()),
        )

        key = '%s&' % oauth.escape(consumer.secret)
        if token:
            key += oauth.escape(token.secret)
        raw = '&'.join(sig)
        return key, raw

    # noinspection PyShadowingNames
    def sign(self, request, consumer, token):
        """Builds the base signature string."""
        key, raw = self.signing_base(request, consumer, token)
        privatekey = keyfactory.parsePrivateKey(self.rsa_private_key)
        signature = privatekey.hashAndSign(bytearray(raw, 'utf8'))

        return base64.b64encode(signature)


def get_jira_oauth_init_parameters():
    config = ConfigParser()
    config.optionxform = str  # Read config file as case insensitive
    config.read(starter_oauth_config_file)
    jira_url = config.get("oauth_config", "jira_base_url")
    consumer_key = config.get("oauth_config", "consumer_key")
    # noinspection PyShadowingNames
    test_jira_issue = config.get("oauth_config", "test_jira_issue")
    rsa_private_key = read_rsa_private_key(path=rsa_private_key_file_path)
    rsa_public_key = read_rsa_public_key(path=rsa_public_key_file_path)

    return {
        "consumer_key": consumer_key,
        "jira_base_url": jira_url,
        "rsa_private_key": rsa_private_key,
        "rsa_public_key": rsa_public_key,
        "test_jira_issue": test_jira_issue
    }


# noinspection PyShadowingNames
def generate_request_token_and_auth_url(base_url, consumer_key, consumer_secret, rsa_private_key):
    request_token_url = base_url + '/plugins/servlet/oauth/request-token'
    authorize_url = base_url + '/plugins/servlet/oauth/authorize'

    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    client = oauth.Client(consumer=consumer)
    client.set_signature_method(SignatureMethod_RSA_SHA1(rsa_private_key=rsa_private_key))

    # Step 1: Get a request token. This is a temporary token that is used for
    # having the user authorize an access token and to sign the request to obtain
    # said access token.
    resp, content = client.request(request_token_url, "POST")
    if resp['status'] != '200':
        raise Exception("Invalid response %s: %s" % (resp['status'], content))

    # If output is in bytes. Let's convert it into String.
    if type(content) == bytes:
        content = content.decode('UTF-8')

    request_token = dict(parse.parse_qsl(content))
    url = f"{authorize_url}?oauth_token={request_token['oauth_token']}"

    return consumer, request_token, url


# noinspection PyShadowingNames
def print_url_and_ask_for_continue(url):
    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.
    print(f"Go to the following link in your browser: {url}")
    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    accepted = 'n'
    while accepted.lower() == 'n':
        accepted = input('Have you authorized me? (y/n) ')


# noinspection PyShadowingNames
def generate_access_token(rsa_private_key, consumer, request_token, access_token_url):
    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(key=request_token['oauth_token'], secret=request_token['oauth_token_secret'])
    # token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer=consumer, token=token)
    client.set_signature_method(SignatureMethod_RSA_SHA1(rsa_private_key=rsa_private_key))

    resp, content = client.request(uri=access_token_url, method="POST")
    # Response is coming in bytes. Let's convert it into String.
    # If output is in bytes. Let's convert it into String.
    if type(content) == bytes:
        content = content.decode('UTF-8')
    return dict(parse.parse_qsl(qs=content))


# noinspection PyShadowingNames
def check_access_token(access_token, consumer, data_url, test_jira_issue):
    print(f"Accessing {test_jira_issue} using generated OAuth tokens:")

    # Now lets try to access the same issue again with the access token. We should get a 200!
    token = oauth.Token(key=access_token['oauth_token'], secret=access_token['oauth_token_secret'])
    client = oauth.Client(consumer=consumer, token=token)
    client.set_signature_method(SignatureMethod_RSA_SHA1(rsa_private_key=rsa_private_key))

    resp, content = client.request(uri=data_url, method="GET")
    if resp['status'] != '200':
        raise Exception("Should have access!")

    print("Success!")
    # If output is in bytes. Let's convert it into String.
    if type(content) == bytes:
        content = content.decode('UTF-8')
    json_content = json.loads(s=content)
    print(f'Issue key: {json_content["key"]}, Summary: {json_content["fields"]["summary"]} ')


if __name__ == '__main__':
    init_dict = get_jira_oauth_init_parameters()
    base_url = init_dict['jira_base_url']
    consumer_key = init_dict["consumer_key"]
    consumer_secret = init_dict["rsa_public_key"]
    rsa_private_key = init_dict['rsa_private_key']
    test_jira_issue = init_dict['test_jira_issue']
    data_url = get_data_url(base_url=base_url, test_jira_issue=test_jira_issue)
    consumer, request_token, url = generate_request_token_and_auth_url(base_url=base_url,
                                                                       consumer_key=consumer_key,
                                                                       consumer_secret=consumer_secret,
                                                                       rsa_private_key=rsa_private_key)
    print(f"Request Token: oauth_token={request_token['oauth_token']}, "
          f"oauth_token_secret={request_token['oauth_token_secret']}")
    print()
    access_token = {'oauth_problem': True}
    while 'oauth_problem' in access_token:
        print_url_and_ask_for_continue(url=url)
        access_token = generate_access_token(rsa_private_key=rsa_private_key,
                                             consumer=consumer,
                                             request_token=request_token,
                                             access_token_url=get_access_token_url(base_url=base_url))
    print()
    print(f"Access Token: oauth_token={access_token['oauth_token']}, "
          f"oauth_token_secret={access_token['oauth_token_secret']}")
    print("You may now access protected resources using the access tokens above.")
    print()
    check_access_token(access_token=access_token, consumer=consumer, data_url=data_url, test_jira_issue=test_jira_issue)
