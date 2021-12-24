import pytumblr2
import oauth2
import sys
import os
import json
import IPython as ipy

from requests_oauthlib import OAuth1Session


def new_oauth(save_path):
    '''
    Return the consumer and oauth tokens with three-legged OAuth process and
    save in a json file in the user's home directory.
    '''

    if os.path.isfile(save_path):
        with open(save_path) as keyfile:
            keys = json.load(keyfile)
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
    else:
        print('Retrieve consumer key and consumer secret from http://www.tumblr.com/oauth/apps')
        consumer_key = input('Paste the consumer key here: ').strip()
        consumer_secret = input('Paste the consumer secret here: ').strip()

    request_token_url = 'http://www.tumblr.com/oauth/request_token'
    authorize_url = 'http://www.tumblr.com/oauth/authorize'
    access_token_url = 'http://www.tumblr.com/oauth/access_token'

    # STEP 1: Obtain request token
    oauth_session = OAuth1Session(consumer_key, client_secret=consumer_secret)
    fetch_response = oauth_session.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    # STEP 2: Authorize URL + Rresponse
    full_authorize_url = oauth_session.authorization_url(authorize_url)

    # Redirect to authentication page
    print('\nPlease go here and authorize:\n{}'.format(full_authorize_url))
    redirect_response = input('Allow then paste the full redirect URL (e.g. localhost:3xxx/etc.) here:\n').strip()

    # Retrieve oauth verifier
    oauth_response = oauth_session.parse_authorization_response(redirect_response)

    verifier = oauth_response.get('oauth_verifier')

    # STEP 3: Request final access token
    oauth_session = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )
    oauth_tokens = oauth_session.fetch_access_token(access_token_url)

    tokens = {
        'consumer_key': consumer_key,
        'consumer_secret': consumer_secret,
        'oauth_token': oauth_tokens.get('oauth_token'),
        'oauth_token_secret': oauth_tokens.get('oauth_token_secret')
    }

    json_file = open(json_path, 'w+')
    json.dump(tokens, json_file, indent=2)
    json_file.close()

    return tokens


def make_client(keyfile_path):
    with open(keyfile_path) as keyfile:
        keys = json.load(keyfile)
    consumer_key = keys['consumer_key']
    consumer_secret = keys['consumer_secret']
    oauth_token = keys['oauth_token']
    oauth_secret = keys['oauth_token_secret']

    client = pytumblr2.TumblrRestClient(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_secret,
        consume_in_npf_by_default=True
    )
    return client


if __name__=="__main__":
    try:
        client = make_client('keys.json')
    except Exception as exc:
        print("Creating new OAuth tokens...")
        new_oauth('keys.json')
        client = make_client('keys.json')

    # returns ratelimit info, from the headers of the most recent API response
    ratelimit = client.get_ratelimit_data()
    print(ratelimit)
