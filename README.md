JIRA OAuth1 Setup and Usage
====================

### Python 3 Setup
* Create Python 3 Virtual Environment
```
mkvirtualenv -p python3 jira_oauth1_py3_env
```
* Activate this environment to work on
```
workon jira_oauth1_py3_env
```
* Install all required libraries
```
pip install -r requirements.txt
```

### RSA Private and Public Key creations
* Make sure you have **.oauthconfig** folder exists in your home directory
* Create RSA Private key and store it in file **oauth.pem**
```
openssl genrsa -out oauth.pem 1024
```
* Create RSA Public Key and store it in file **oauth.pub**
```
openssl rsa -in oauth.pem -pubout -out oauth.pub
```
* Again make sure both files are *copied* to **.oauthconfig** folder in your home directory.
* Also share RSA Public Key **oauth.pub** with your Jira Admin, as they need it during _Jira Application Link_ creation.


### Jira Application Link Creation Steps
* Logon as a Jira Administrator
* Go to **Application links** section under **Application** area
* Enter dummy url (as oauth token used for API access and not web access) *https://jira-oauth1-rest-api-access*
* Click on **Create new link** button
* Click **Continue** on next screen
* Enter something like **Jira OAuth1 REST API access** as a *Application Name*
* Don't need to fill any other information. Click on **Continue**
* Now you should able to see new Application link with name **Jira OAuth1 REST API access** created and available under section *Configure Application Links* section
* Click on *pencil* icon to configure **Incoming Authentication**
  * Enter **jira-oauth1-rest-api-access** (or any other appropriate string) as *Consumer Key*
  * Enter same string **jira-oauth1-rest-api-access** (or any other appropriate string) as *Consumer Name*
  * Enter content of RSA Public key (stored in file **oauth.pub**) as **Public Key**
  * Click on **Save**

### Prepare for OAuth Dance
Create **starter_oauth.config** in **~/.oauthconfig** folder:
```ini
[oauth_config]
jira_base_url=https://jira.example.com
consumer_key=jira-oauth1-rest-api-access
test_jira_issue=EXJIRA-123
```

Perform Jira OAuth Dance
================
* Make sure you are in base directory of this Repo
* Python Virtual Environment that we create earlier is active.
* Run **jira_oauth_token_generator.py**
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/jira_oauth_token_generator.py
```
* Authenticate in browser as directed below and then click **y** for question *Have you authorized me?*
* After successful oAuth generation, you will get another set of values for **oauth_token** and **oauth_token_secret**. These are you tokens that you need to use access Jira without passing credentials.
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/jira_oauth_token_generator.py
Request Token: oauth_token=6AOSSREyS9HaACqEcHjcD6RJVms2NjEr, oauth_token_secret=gnpJMfbgUyG8W4dKzFW4PKFbGttV2CWm

Go to the following link in your browser: https://jira.example.com/plugins/servlet/oauth/authorize?oauth_token=6AOSSREyS9HaACqEcHjcD6RJVms2NjEr
Have you authorized me? (y/n) y

Access Token: oauth_token=lmOh7LEdvZ2yxKIm5rdQY2ZfZqNdvUV4, oauth_token_secret=gnpJMfbgUyG8W4dKzFW4PKFbGttV2CWm
You may now access protected resources using the access tokens above.

Accessing IDEV-1 using generated OAuth tokens:
Success!
Issue key: IDEV-1, Summary: Internal Devepment Issue #1
```

## Copy both oauth_token and oauth_token_secret to .oauth_jira_config.<jira_env> file.
```
(jira_oauth1_py3_env) ➜  .oauthconfig cat .oauth_jira_config.dev
[oauth_token_config]
oauth_token=sdfPxIsdfsdfs$sdf234sdgssd$sresdf
oauth_token_secret=rswfsdfsdfjsdjlksjdfljsdlkfjsldfj
consumer_key=jira-export-rest-api-access
user_private_key_file_name=oauth.pem

[server_info]
jira_base_url=https://jira-dev.teslamotors.com

[jira_oauth_generator]
test_issue_key=ITDOS-145
```

### Using OAuth1 tokens in Sample Jira Script.
* Using Python Requests library
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/access_using_requests_package.py dev
(EXJIRA) Excitement for JIRA Project People
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗
```
* Using Python JIRA library
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_generator/access_using_jira_library.py prod
Reteriving Issue: ITEST-145
Issue:ITEST-145, Summary: Test access request
Reteriving 1st three Jira Projects available to you:
First 3 Projects are ['TES', 'TEst', 'TEST']
```

>Original implementation is available here:
>
> https://bitbucket.org/atlassian_tutorial/atlassian-oauth-examples under python/app.py
