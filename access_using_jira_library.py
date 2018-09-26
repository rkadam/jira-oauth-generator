from jira import JIRA
from configparser import SafeConfigParser
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("final_oauth_token_file_path", help = "Enter complete file path for final_oauth_token.config")
args = parser.parse_args()

config = SafeConfigParser()
config.read(args.final_oauth_token_file_path)
jira_url = config.get("final_oauth_config", "jira_base_url")
oauth_token = config.get("final_oauth_config", "oauth_token")
oauth_token_secret=config.get("final_oauth_config", "oauth_token_secret")
consumer_key = config.get("final_oauth_config", "consumer_key")
test_issue_key = config.get("final_oauth_config", "test_issue_key")

if jira_url[-1] == '/':
	jira_url = jira_url[0:-1]

key_cert_data = None
path = os.path.dirname(os.path.abspath(__file__))
# Load Private Key file from "config" directory.
with open( path + '/config/oauth.pem', 'r') as key_cert_file:
    key_cert_data = key_cert_file.read()
    
oauth_dict = {
    'access_token' : oauth_token,
    'access_token_secret': oauth_token_secret,
    'consumer_key': consumer_key,
    'key_cert': key_cert_data
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