import requests
import datetime

def getNestedComments(replies, root_node, convo_dict):
    for i in range(len(replies)):
        reply = replies[i]
        if 'created_utc' in reply['data'] and 'parent_id' in reply['data'] and 'body' in reply['data'] and '[deleted]' not in reply['data']['body']:
            print('User:', reply['data']['id'])
            print('Time:', datetime.datetime.fromtimestamp(reply['data']['created_utc']))
            print('In reply to:', reply['data']['parent_id'][3:])
            print(reply['data']['body'], '\n')
            
            convo_dict['user_name'].append(reply['data']['author'])
            convo_dict['id'].append(reply['data']['id'])
            convo_dict['timestamp'].append(datetime.datetime.fromtimestamp(reply['data']['created_utc']))
            convo_dict['reply_to'].append(reply['data']['parent_id'][3:])
            convo_dict['comment'].append(reply['data']['body'])
            
            child = Node(reply['data']['id'], parent=root_node)

            if 'replies' in reply['data'] and reply['data']['replies'] != '':
                getNestedComments(reply['data']['replies']['data']['children'], child, convo_dict)

        else:
            return
        
def createTree(res, post_id):
    root = Node(post_id)
    comments = res.json()[1]['data']['children']
    
    conversation_dict = {'user_name':[], 'id':[], 'timestamp':[], 'reply_to':[], 'comment':[]}

    print('-----About the post-----')
    print('No. of Upvotes:', res.json()[0]['data']['children'][0]['data']['ups'])
    print('Upvote Ratio:', res.json()[0]['data']['children'][0]['data']['upvote_ratio'], '\n')

    for i in range(len(comments)):
        comment = comments[i]
        try:
            if '[deleted]' not in comment['data']['body']:

                print('User:', comment['data']['id'], 
                      'Time:', datetime.datetime.fromtimestamp(comment['data']['created_utc']))
                print('In reply to:', comment['data']['parent_id'][3:])
                print(comment['data']['body'], '\n')

                conversation_dict['user_name'].append(comment['data']['author'])
                conversation_dict['id'].append(comment['data']['id'])
                conversation_dict['timestamp'].append(datetime.datetime.fromtimestamp(comment['data']['created_utc']))
                conversation_dict['reply_to'].append(comment['data']['parent_id'][3:])
                conversation_dict['comment'].append(comment['data']['body'])

                child = Node(comment['data']['id'], parent=root)

                if comment['data']['replies'] != '':
                    replies = comment['data']['replies']['data']['children']

                    getNestedComments(replies, child, conversation_dict)
                    
        except:
            continue
            
    return conversation_dict, root

def getRedditPosts(subreddit):
    all_posts = requests.get(f'https://api.pushshift.io/reddit/search/submission/?subreddit={subreddit}&sort=desc&sort_type=created_utc&size=50')

    for i in range(len(all_posts.json()['data'])):
        post = all_posts.json()['data'][i]
        print('Post ID:', post['id'], 
              'Time:', datetime.datetime.fromtimestamp(post['created_utc']))
        print(post['title'], '\n')

    #     command = (
    #             '''
    #             INSERT INTO reddit_data
    #             VALUES ('%s', '%s', '%s');
    #             ''' % (post['id'], datetime.datetime.fromtimestamp(post['created_utc']), 
    #                    post['title'])
    #             )
    #     setUpDB(command, uri)