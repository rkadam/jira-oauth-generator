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


# noinspection PyPep8Naming
class SignatureMethod_RSA_SHA1(oauth.SignatureMethod):
    name = 'RSA-SHA1'

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

    def sign(self, request, consumer, token):
        """Builds the base signature string."""
        key, raw = self.signing_base(request, consumer, token)

        # Load RSA Private Key
        with open(Path.home() / '.oauthconfig/oauth.pem', 'r') as f:
            data = f.read()
        privateKeyString = data.strip()

        privatekey = keyfactory.parsePrivateKey(privateKeyString)

        '''
            We were getting errors on encoding, so added explicitly "utf8" encoding in rsakey.py
            In function hashAndSign(...),
                *changed line* ->   hashBytes = SHA1(bytearray(bytes))
                to ->               hashBytes = SHA1(bytearray(bytes, "utf8"))
        '''
        signature = privatekey.hashAndSign(raw)

        return base64.b64encode(signature)


def get_jira_oauth_init_parameters():
    # Assumption "starter_auth.config" file is stored in ~/.oauthconfig/ directory
    starter_oauth_config_file = Path.home() / ".oauthconfig/starter_oauth.config"

    config = ConfigParser()
    config.optionxform=str # Read config file as case insensitive
    config.read(starter_oauth_config_file)
    jira_url = config.get("oauth_config", "jira_base_url")
    consumer_key = config.get("oauth_config", "consumer_key")
    test_jira_issue = config.get("oauth_config","test_jira_issue")

    with open(Path.home() / '.oauthconfig/oauth.pub', 'r') as key_cert_file:
        rsa_public_key = key_cert_file.read()

    return {
        "consumer_key": consumer_key,
        "jira_base_url": jira_url,
        "rsa_public_key": rsa_public_key,
        "test_jira_issue": test_jira_issue
    }


def generate_oauth_token():
    init_dict = get_jira_oauth_init_parameters()
    consumer_key = init_dict["consumer_key"]
    consumer_secret = init_dict["rsa_public_key"]
    test_jira_issue = init_dict["test_jira_issue"]

    base_url = init_dict["jira_base_url"]
    request_token_url = base_url + '/plugins/servlet/oauth/request-token'
    access_token_url = base_url + '/plugins/servlet/oauth/access-token'
    authorize_url = base_url + '/plugins/servlet/oauth/authorize'

    data_url = base_url + f'/rest/api/2/issue/{test_jira_issue}?fields=summary'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    client.disable_ssl_certificate_validation = True

    # Lets try to retrieve mentioned Jira issue
    resp, content = client.request(data_url, "GET")

    '''
    # As per original code, we should get 401, but browser returns 200.
    if resp['status'] != '401':
        raise Exception("Should have no access!")
    '''

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

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
    print("Request Token:")
    print(f"    - oauth_token        = {request_token['oauth_token']}")
    print("    - oauth_token_secret = %s" % request_token['oauth_token_secret'])
    print("")

    # Step 2: Redirect to the provider. Since this is a CLI script we do not
    # redirect. In a web application you would redirect the user to the URL
    # below.

    print("Go to the following link in your browser:")
    print("%s?oauth_token=%s" % (authorize_url, request_token['oauth_token']))
    print()

    # After the user has granted access to you, the consumer, the provider will
    # redirect you to whatever URL you have told them to redirect to. You can
    # usually define this in the oauth_callback argument as well.
    accepted = 'n'
    while accepted.lower() == 'n':
        accepted = input('Have you authorized me? (y/n) ')
    # oauth_verifier = raw_input('What is the PIN? ')

    # Step 3: Once the consumer has redirected the user back to the oauth_callback
    # URL you can request the access token the user has approved. You use the
    # request token to sign this request. After this is done you throw away the
    # request token and use the access token returned. You should store this
    # access token somewhere safe, like a database, for future use.
    token = oauth.Token(request_token['oauth_token'],
                        request_token['oauth_token_secret'])
    # token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    resp, content = client.request(access_token_url, "POST")
    # Response is coming in bytes. Let's convert it into String.
    # If output is in bytes. Let's convert it into String.
    if type(content) == bytes:
        content = content.decode('UTF-8')
    access_token = dict(parse.parse_qsl(content))

    print("Access Token:")
    print("    - oauth_token        = %s" % access_token['oauth_token'])
    print("    - oauth_token_secret = %s" % access_token['oauth_token_secret'])
    print("")
    print("You may now access protected resources using the access tokens above.")
    print("")

    print("")
    print(f"Accessing {test_jira_issue} using generated OAuth tokens:")
    print("")
    # Now lets try to access the same issue again with the access token. We should get a 200!
    accessToken = oauth.Token(access_token['oauth_token'],
                              access_token['oauth_token_secret'])
    client = oauth.Client(consumer, accessToken)
    client.set_signature_method(SignatureMethod_RSA_SHA1())

    resp, content = client.request(data_url, "GET")
    if resp['status'] != '200':
        raise Exception("Should have access!")

    print("Success!")
    # If output is in bytes. Let's convert it into String.
    if type(content) == bytes:
        content = content.decode('UTF-8')
    json_content = json.loads(content)
    print(f'Issue key: {json_content["key"]}, Summary: {json_content["fields"]["summary"]} ')
    print("")


if __name__ == '__main__':
    generate_oauth_token()
