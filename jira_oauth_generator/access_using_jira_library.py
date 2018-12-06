from jira import JIRA
from configparser import ConfigParser
import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("jira_environment", help = "Enter Jira Environment where you want to run this library. Options: dev/prod")
args = parser.parse_args()

print()
print(f"Reading OAuth from {Path.home()}/.oauthconfig/.oauth_jira_config.{args.jira_environment}")

config = ConfigParser()
config.read(Path.home() / f".oauthconfig/.oauth_jira_config.{args.jira_environment}")
jira_url = config.get("server_info", "jira_base_url")

oauth_token = config.get("oauth_token_config", "oauth_token")
oauth_token_secret=config.get("oauth_token_config", "oauth_token_secret")
consumer_key = config.get("oauth_token_config", "consumer_key")

test_issue_key = config.get("jira_oauth_generator", "test_issue_key")

rsa_private_key = None
# Load RSA Private Key file.
with open( Path.home() /'.oauthconfig/oauth.pem', 'r') as key_cert_file:
    rsa_private_key = key_cert_file.read()

if jira_url[-1] == '/':
	jira_url = jira_url[0:-1]

oauth_dict = {
    'access_token' : oauth_token,
    'access_token_secret': oauth_token_secret,
    'consumer_key': consumer_key,
    'key_cert': rsa_private_key
}

ajira = JIRA(oauth=oauth_dict, server = jira_url)
print("")
print(f"Reteriving Issue: {test_issue_key}")
issue = ajira.issue(test_issue_key, fields ='summary,comment')
print (f"Issue:{test_issue_key}, Summary: {issue.fields.summary}")
print("")

print("Reteriving 1st three Jira Projects available to you:")
projects = ajira.projects()
keys = sorted([project.key for project in projects])[2:5]
print("First 3 Projects are %s" %keys)
print("")