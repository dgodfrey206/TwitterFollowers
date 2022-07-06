import requests
from requests.adapters import HTTPAdapter, Retry
import pandas as pd
import yaml
import json
import os

# Enable this to debug all http connections
# import http
# http.client.HTTPConnection.debuglevel = 1

def load_config():
    with open(os.getcwd()+"/config.yaml") as f:
        try:
            yaml_config = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            print(exc)
            print("Could not load config.yaml")
            exit()
    return yaml_config

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def find_user_by_username(username):
    endpoint_url = f"https://api.twitter.com/2/users/by/username/{username}"
    return endpoint_url

def parse_user_by_username(response_user_by_username):
    json_user_by_username = response_user_by_username.json()
    if 'errors' in json_user_by_username:
        print(f"{json_user_by_username['errors'][0]['title']}: {json_user_by_username['errors'][0]['detail']}")
        exit()
    elif 'data' in json_user_by_username:
        print(f"Found user {json_user_by_username['data']['username']} with id {json_user_by_username['data']['id']}.")
        return json_user_by_username['data']['id']

def get_users_following(user_id):
    endpoint_url = f"https://api.twitter.com/2/users/{user_id}/following"
    return endpoint_url

def get_users_followers(user_id):
    endpoint_url = f"https://api.twitter.com/2/users/{user_id}/followers"
    return endpoint_url

def get_responses_paginated(endpoint_url, req_session):
    query_params = {'max_results':1000,
                    'pagination_token': None
                    }
    data_df = None
    while(True):
        response_json = req_session.get(endpoint_url,params=query_params).json()
        # print(response_json)
        if 'data' in response_json:
            # responses_list.append(response_json['data'])
            if data_df is None:
                data_df = pd.json_normalize(response_json['data'])
            else:
                temp_df = pd.json_normalize(response_json['data'])
                data_df = pd.concat([data_df, temp_df],ignore_index=True)

        if 'meta' in response_json:
            response_meta = response_json['meta']
            if 'next_token' in response_meta:
                next_token = response_json['meta']['next_token']
                query_params['pagination_token'] = next_token
            else:
                break
        elif 'status' in response_json:
            if response_json['status'] == 429:
                pass
        else:
            break
    return data_df
if __name__ == "__main__":
    config = load_config()

    try:
        bearer_token = config['bearer']
        save_txt = config['save_txt']
        save_csv = config['save_csv']
    except:
        print("Please check config.yaml for bearer, save_txt, and save_csv")
        exit()

    # Set up requests session for retries and exponential backoff
    req_session = requests.Session()
    retries = Retry(total=10,
                    backoff_factor=2,
                    status_forcelist=[ 429, 500, 502, 503, 504 ])
    req_session.mount('http://', HTTPAdapter(max_retries=retries))
    req_session.mount('https://', HTTPAdapter(max_retries=retries))

    # set session headers for Authorization
    headers = create_headers(bearer_token)
    req_session.headers.update(headers)

    twitter_profile_url = str(input("Enter a twitter profile url: "))
    twitter_profile_url = twitter_profile_url.split('/')
    twitter_profile = twitter_profile_url[-1]
    print(f"Looking up user '{twitter_profile}'.")
    response_user_by_username = req_session.get(find_user_by_username(twitter_profile))
    user_id = parse_user_by_username(response_user_by_username)
    response_user_followers_df = get_responses_paginated(get_users_followers(user_id), req_session)
    response_user_following_df = get_responses_paginated(get_users_following(user_id), req_session)
    if(save_csv):
        response_user_followers_df.to_csv(f"{twitter_profile}_followers.csv", index=False)
        response_user_following_df.to_csv(f"{twitter_profile}_following.csv", index=False)
    if(save_txt):
        response_user_followers_df['username'].to_csv(f"{twitter_profile}_followers.txt", index=False)
        response_user_following_df['username'].to_csv(f"{twitter_profile}_following.txt", index=False)
    # print(f"User {twitter_profile} with")
