'''
Sample program demnostrating how to access Jira using OAuth1 tokens and Requests library!
* It reads list of projects available to user and prints name of first project
* Adds comment on given Issue with test_issue_key
'''

from configparser import ConfigParser
import argparse
import requests
from requests_oauthlib import OAuth1
import os
from pathlib import Path

def get_jira_oauth_init_parameters(jira_env):

    config = ConfigParser()
    print()
    print(f"Reading OAuth from {Path.home()}/.oauthconfig/.oauth_jira_config.{jira_env}")
    config.read(Path.home() / f".oauthconfig/.oauth_jira_config.{jira_env}")

    jira_url = config.get("server_info", "jira_base_url")

    oauth_token = config.get("oauth_token_config", "oauth_token")
    oauth_token_secret=config.get("oauth_token_config", "oauth_token_secret")
    consumer_key = config.get("oauth_token_config", "consumer_key")

    test_issue_key = config.get("jira_oauth_generator", "test_issue_key")

    rsa_private_key = None
    # Load RSA Private Key file.
    with open( Path.home() /'.oauthconfig/oauth.pem', 'r') as key_cert_file:
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

    parser = argparse.ArgumentParser()
    parser.add_argument("jira_environment", help = "Enter Jira Environment where you want to run this library. Options: dev/prod")
    args = parser.parse_args()

    init_dict = get_jira_oauth_init_parameters(args.jira_environment)
    base_url = init_dict["jira_url"]
    test_issue_key = init_dict["test_issue_key"]

    jira_session = get_jira_session(init_dict)

    # Get 1st Jira Project Name
    get_jira_projects(jira_session, base_url)

    # Add comment to given issue
    add_comment_to_issue(jira_session, base_url, test_issue_key)