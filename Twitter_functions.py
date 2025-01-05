import requests
import pandas as pd
from functions import *

########## Functions to obtain tweets and other details from API ##########

# Create authentication key to access Twitter API
def create_Twitter_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

with open('Authentication/twitter_bearer_token.txt', 'r', encoding="utf8") as f:
    token = f.read()

header = create_Twitter_headers(token)

# Connect to API with authentication key
def connect_to_endpoint(url, headers, next_token = None):    
    response = requests.request("GET", url, headers = headers)
        
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        
    return response.json()

# Obtain the tweets and replies of a specific user
def getTweetsByUserID(user_id, header, max_results = 100):
    tweets_url = f'https://api.twitter.com/2/users/{user_id}/tweets?max_results={max_results}'
    return connect_to_endpoint(tweets_url, header)
    
# Obtain the information relating to a specific tweet
def getSingleTweetInfo(tweetID, header):
    params = 'created_at,conversation_id,in_reply_to_user_id,author_id,referenced_tweets'
    tweets_url = f'https://api.twitter.com/2/tweets?tweet.fields={params}&ids={tweetID}'
    return connect_to_endpoint(tweets_url, header)

# Obtain information relating to specific account
def getTwitterUserInfo(username, header):
    user_result = f'https://api.twitter.com/2/users/by?usernames={username}&user.fields=created_at&expansions=pinned_tweet_id&tweet.fields=author_id,created_at'
    return connect_to_endpoint(user_result, header)
    
# View the tweets liked by a specific user
def getTweetsLikedByUser(userID, header, max_results = 100):
    user_result = f'https://api.twitter.com/2/users/{userID}/liked_tweets?max_results={max_results}'
    return connect_to_endpoint(user_result, header)

# 'conversation_id' is the identifier for the main tweet
# Get all comments of tweet
def getConversation(conversation_id, header, max_results = 100):
    params = 'in_reply_to_user_id,author_id,created_at,conversation_id'
    getConversation_url = f'https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{conversation_id}&tweet.fields={params}&max_results={max_results}'
    return connect_to_endpoint(getConversation_url, header)

############### Data processing functions ###############

# Process tweet comments into a dictionary
def processTweetsToDict(conversation_data):
    track_id = 10000
    conversation_dict = {'id':[], 'timestamp':[], 'reply_to':[], 'comment':[], 'new_id':[]} #
    
    for i in range(len(conversation_data['data'])):
        print('User ID:', conversation_data['data'][i]['author_id'], 
              'Time:', conversation_data['data'][i]['created_at'])
        print('In reply to:', conversation_data['data'][i]['in_reply_to_user_id'])
        print(conversation_data['data'][i]['text'], '\n')
        
        conversation_dict['id'].append(conversation_data['data'][i]['author_id'])
        conversation_dict['timestamp'].append(conversation_data['data'][i]['created_at'])
        conversation_dict['reply_to'].append(conversation_data['data'][i]['in_reply_to_user_id'])
        conversation_dict['comment'].append(conversation_data['data'][i]['text'])
        conversation_dict['new_id'].append(track_id)
        
        track_id += 1
        
    return conversation_dict

# Obtain the identifier of user that comment is being replied to
def getParentID(dataframe, parent_tweet_id):
    parent_id = []

    for index, row in dataframe.iterrows():
        if row['reply_to'] != parent_tweet_id:
            count = 0
            
            for _, i in dataframe.iterrows():
                if row['reply_to'] == i['id']:
                    parent_id.append(i['new_id'])
                    truth = True
                    break

                count += 1

            if count == len(dataframe):
                parent_id.append('nan')
        
        else:
            parent_id.append(parent_tweet_id)
            
    return parent_id

# Convert JSON structure of output of API to a printed information
def generateTweetInformation(dataset, header):
    
    for i in range(len(dataset['data'])):
        print('Tweet ID:', dataset['data'][i]['id'], 
              'Time:', getSingleTweetInfo(dataset['data'][i]['id'], header)['data'][0]['created_at'])
        print(dataset['data'][i]['text'], '\n')
    
# Process tweet data in dictionary form to a structured dataframe and save data to database
def processTwitterDataframe(result_dict, account_id, conversation_id, uri, saveDF = True):
    df = pd.DataFrame.from_dict(result_dict)
    df['id'] = df['id'].astype(str)
    df['reply_to'] = df['reply_to'].astype(str)
    df['reply_to_id'] = getParentID(df, account_id)
    df['social_media'] = 'Twitter'
    df['conversation_id'] = conversation_id
    df['head_id'] = account_id
    df['user_id'] = df['id']
    df['id'] = df['new_id']
    df['reply_to'] = df['reply_to_id']
    df = df.drop(columns=['new_id', 'reply_to_id'])
    
    query = ('''
        select * from comments_for_analysis where conversation_id = '%s'
    ''' % df['conversation_id'][0])
    data = getData(query, uri)
    
    if len(data) == 0:
        for index, row in df.iterrows():
            command = (
                    '''
                    INSERT INTO comments_for_analysis
                    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');
                    ''' % (row['id'], row['timestamp'], row['reply_to'], row['comment'].replace("'", "''"), row['social_media'], row['head_id'], str(row['conversation_id']), row['user_id'])
                    )
            setUpDB(command, uri)
            
    else:
        print('Conversation has been updated in the database.')
    
    
    df['url'] = df['comment'].apply(lambda x: getLinks(x))
    df['link_title'] = df['url'].apply(lambda x: getURLfromList(x))

    if saveDF:
        df.to_csv(f'Datasets/twitter_data_{conversation_id}.csv', index=False)
        
    return df    