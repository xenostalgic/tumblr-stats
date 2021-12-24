import pytumblr2
import sys

client = make_client('keys.txt')

def make_client(keyfile_path):
    keys = []
    for line in open(keyfile_path):
        keys.append(line.strip())
    client = pytumblr2.TumblrRestClient(
        keys[0] # consumer_key
        keys[1] # consumer_secret
        keys[2] # oauth_token
        keys[3] # oauth_secret
        consume_in_npf_by_default=True
    )
    return client

    

# returns ratelimit info, from the headers of the most recent API response
client.get_ratelimit_data()

if __name__=="__main__":
    
