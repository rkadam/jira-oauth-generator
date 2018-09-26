'''
Sample program demnostrating how to access Jira using OAuth1 tokens and Requests library!
* It reads list of projects available to user and prints name of first project
* Adds comment on given Issue with test_issue_key
'''

import configparser
import argparse
import requests
from requests_oauthlib import OAuth1
import os

def get_jira_oauth_init_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument("final_oauth_token_config_file", help = "Enter complete file path for final_oauth_token.config")
    args = parser.parse_args()

    config = configparser.SafeConfigParser()
    config.read(args.final_oauth_token_config_file)
    jira_url = config.get("final_oauth_config", "jira_base_url")

    oauth_token = config.get("final_oauth_config", "oauth_token")
    oauth_token_secret=config.get("final_oauth_config", "oauth_token_secret")
    consumer_key = config.get("final_oauth_config", "consumer_key")
    test_issue_key = config.get("final_oauth_config", "test_issue_key")

    rsa_private_key = None
    path = os.path.dirname(os.path.abspath(__file__))
    # Load Private Key file from "config" directory.
    with open( path + '/config/oauth.pem', 'r') as key_cert_file:
        rsa_private_key = key_cert_file.read()

    oauth = OAuth1(client_key = consumer_key,
        rsa_key = rsa_private_key,
        signature_method='RSA-SHA1',
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret
    )

    return {
        "oauth1_object" : oauth,
        "jira_url" : jira_url,
        "test_issue_key": test_issue_key
    }

def get_jira_session(init_dict):
    session = requests.Session()
    session.auth = init_dict["oauth1_object"]
    session.headers.update({'X-Atlassian-Token': 'nocheck'})
    return session    

def get_jira_projects(session, base_url):
    print("")
    print("Reteriving 1st Jira Project available to you:")
    jira_projects_url =  base_url + '/rest/api/2/project'
    response = jira_session.get(jira_projects_url)
    response.raise_for_status()
    # Get First Project name from list of Projects reterived.
    print(response.json()[0]['name'])
    print("")

def add_comment_to_issue(session, base_url, issue_key):
    print("")
    print(f"Adding comment to issue {issue_key}")
    try:
        post_data_dict = {}
        post_data_dict["body"] = "This is a test comment using bare REST api."
        post_result = session.post(f"{base_url}/rest/api/2/issue/{issue_key}/comment", 
                                    json = post_data_dict)
        post_result.raise_for_status()
        print("Comment successfully added. Please verify through browser!")
        print("")
    except requests.exceptions.HTTPError as err:
        print (err)    

if __name__ == "__main__":

    init_dict = get_jira_oauth_init_parameters()
    base_url = init_dict["jira_url"]
    test_issue_key = init_dict["test_issue_key"]

    jira_session = get_jira_session(init_dict)

    # Get 1st Jira Project Name
    get_jira_projects(jira_session, base_url)

    # Add comment to given issue
    add_comment_to_issue(jira_session, base_url, test_issue_key)