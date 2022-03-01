import requests

def connect_to_endpoint(url, headers, next_token = None):    
    response = requests.request("GET", url, headers = headers)
        
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
        
    return response.json()

def create_Twitter_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def getTweets(user_id, header):
    tweets_url = f'https://api.twitter.com/2/users/{user_id}/tweets'
    return connect_to_endpoint(tweets_url, header)

# 'conversation_id' is the identifier for the main tweet
def getConversation(conversation_id, max_results, header):
    params = 'in_reply_to_user_id,author_id,created_at,conversation_id'
    getConversation_url = f'https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{conversation_id}&tweet.fields={params}&max_results={max_results}'

    return connect_to_endpoint(getConversation_url, header)

# For now we will return the time only
def getTweetInformation(conversation_id, header):
    params = 'created_at,conversation_id,in_reply_to_user_id,author_id,referenced_tweets'
    tweetInfo_url = f'https://api.twitter.com/2/tweets?tweet.fields={params}&ids={conversation_id}'
    
    result = connect_to_endpoint(tweetInfo_url, header)
    return result['data'][0]['created_at']

def getTweetComments(conversation_data):
    conversation_dict = {'id':[], 'timestamp':[], 'reply_to':[], 'comment':[]} #, 'new_id':[]
    
    for i in range(len(conversation_data['data'])):
        print('User ID:', conversation_data['data'][i]['author_id'], 
              'Time:', conversation_data['data'][i]['created_at'])
        print('In reply to:', conversation_data['data'][i]['in_reply_to_user_id'])
        print(conversation_data['data'][i]['text'], '\n')
        
        conversation_dict['id'].append(conversation_data['data'][i]['author_id'])
        conversation_dict['timestamp'].append(conversation_data['data'][i]['created_at'])
        conversation_dict['reply_to'].append(conversation_data['data'][i]['in_reply_to_user_id'])
        conversation_dict['comment'].append(conversation_data['data'][i]['text'])
#         conversation_dict['new_id'].append(generateRandomID())
        
    return conversation_dict