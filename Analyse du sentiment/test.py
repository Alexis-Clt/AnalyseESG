import Credentials
import tweepy

def getClient():

    client = tweepy.Client(
        bearer_token = Credentials.BEARER_TOKEN,
        consumer_key = Credentials.CONSUMER_KEY,
        consumer_secret = Credentials.CONSUMER_SECRET,
        access_token = Credentials.ACCESS_TOKEN,
        access_token_secret = Credentials.ACCESS_TOKEN_SECRET)

    return client

client = getClient()
print(client.get_me())