JIRA OAuth1 Setup and Usage
====================

### Python 3 Setup
* Create Python 3 Virtual Environment (**Verified against Python 3.6.6**!)
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
* Configure **starter_oauth.config** with correct values
  * jira_base_url=https://jira.example.com
  * consumer_key=jira-oauth1-rest-api-access
  * test_jira_issue=EXJIRA-123

Perform Jira OAuth Dance
================
* Make sure you are in base directory of this Repo
* Python Virtual Environment that we create earlier is active.
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ ls -1
README.md
access_using_requests_package.py
config
jira_oauth_token_generator.py
requirements.txt
```
* Run **jira_oauth_token_generator.py**
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_token_generator.py
```
* If you get TypeError, **string argument without an encoding** as below, you need to update **hashAndSign** function in rsakey.py where package is installed as shown in path below.
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_token_generator.py
...
/../jira_oauth1_py3_env/lib/python3.6/site-packages/tlslite/utils/rsakey.py", line 62, in hashAndSign
    hashBytes = SHA1(bytearray(bytes))
TypeError: string argument without an encoding
```
  * To fix this error, add explicitly "utf8" encoding in rsakey.py in hashAndSign function
```
In function hashAndSign(...),
    *changed line* ->   hashBytes = SHA1(bytearray(bytes))
    to ->               hashBytes = SHA1(bytearray(bytes, "utf8"))
```
* Authenticate in browser as directed below and then click **y** for question *Have you authorized me?*
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python jira_oauth_token_generator.py

Token:
    - oauth_token        = sdfsdf2342edfsdfwfwfwer23432423    
    - oauth_token_secret = sdfsdf2345t66w54564336sdgwtwte

Go to the following link in your browser:
https://jira.example.com/plugins/servlet/oauth/authorize?oauth_token=O2hfcGETBfKpxpvB5L6WzQc4dwaxGCPe
Have you authorized me? (y/n)
```
* After successful oAuth generation, you will get another set of values for **oauth_token** and **oauth_token_secret**. These are you tokens that you need to use access Jira without passing credentials.
> Access Token:
>    - oauth_token        = sdfPxIsdfsdfs$sdf234sdgssd$sresdf
>    - oauth_token_secret = rswfsdfsdfjsdjlksjdfljsdlkfjsldfj
>
> You may now access protected resources using the access tokens above.
>
>
> Accessing JIRA-123 using generated OAuth tokens:
>
> Success!
>
> Issue key: JIRA-123, Summary: This is JIRA-123 Summary

## Copy both oauth_token and oauth_token_secret to .oauth_jira_config.<jira_env> file.
```
(jira_oauth1_py3_env) ➜  .oauthconfig cat .oauth_jira_config.dev
[oauth_token_config]
oauth_token=sdfPxIsdfsdfs$sdf234sdgssd$sresdf
oauth_token_secret=rswfsdfsdfjsdjlksjdfljsdlkfjsldfj
consumer_key=jira-export-rest-api-access
user_private_key_file_name=oauth.pem

[server_info]
jira_base_url=https://jira-dev.example.com

[jira_oauth_generator]
test_issue_key=JIRA-123
```

### Using OAuth1 tokens in Sample Jira Script.
* Using Python Requests library
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python access_using_requests_package.py dev
(EXJIRA) Excitement for JIRA Project People
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗
```
* Using Python JIRA library
```
(jira_oauth1_py3_env) ➜  jira-oauth-generator git:(master) ✗ python access_using_jira_library.py prod
Reteriving Issue: JIRA-123
Issue:JIRA-123, Summary: Test access request
Reteriving 1st three Jira Projects available to you:
First 3 Projects are ['TES', 'TEst', 'TEST']
```

>Original implementation is available here: 
>
> https://bitbucket.org/atlassian_tutorial/atlassian-oauth-examples under python/app.py
