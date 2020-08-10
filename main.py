import requests 
from datetime import datetime
import matplotlib.pyplot as plt
from time import sleep
import json

# Customize Colors for matplotlib
CB91_Blue = '#2CBDFE'
CB91_Green = '#47DBCD'
CB91_Pink = '#F3A0F2'
CB91_Purple = '#9D2EC5'
CB91_Violet = '#661D98'
CB91_Amber = '#F5B14C'

color_list = [CB91_Violet, CB91_Pink, CB91_Green, CB91_Amber,
              CB91_Purple, CB91_Blue]

# Constants
# UTC Timestamp of MODs post on ban 
BAN_UTC = 1596412800
BAN_DATE = datetime.fromtimestamp(BAN_UTC).date()


def getPostAndCommentCount(start, subreddit="animemes"):
    """
    Get the number of Posts and comments on a given 24 hr period.
    @param: start: The start of 24 hr period in UNIX Timestamp
    @param: subreddit: The subreddit to search for
    @return: tuple in format (post_counts, comments_counts)
    """
    end = start + 86400 # Seconds in a day
    count_post = 0
    count_comments =0
    while start<end:

        req = requests.get("https://api.pushshift.io/reddit/search/submission/?after={}&subreddit={}&before={}&fields=created_utc,num_comments&size=500".format(start, subreddit, end))
        if req.status_code != 200:
            raise APIError('Invalid Response Code by API. Got Status Code: ', req.status_code)
        
        raw_data = req.json()['data']
        if raw_data is None or len(raw_data) == 0:
            start += 60*5 # Jump forwad five minutes
            continue 
        count_post += len(raw_data)
        for post in raw_data:
            count_comments += post['num_comments']
        
        start = raw_data[-1]['created_utc']
        # So that API server doesnt get load
        sleep(0.6 )
    return count_post, count_comments

def fetchDataReddit(search, typ = "COMMENTS", days = 30, subreddit = "animemes"):
    """
    Makes an aggregation query for past `days` with comments and post containing search query
    @params: type : "COMMENTS" | "POSTS"
    @params: search: The term that needs to be searched
    @params: days: The number of past days need to be searched 
    @params : subreddit : The subreddit to be searched for
    """

    if typ != "COMMENTS" and typ != "POSTS":
        raise ValueError("typ can be COMMENTS or POSTS only")

    if typ == "COMMENTS":
        typ = "comment"
    else:
        typ = "submission"
    
    req = requests.get("https://api.pushshift.io/reddit/search/{}/?q={}&after={}d&aggs=created_utc&frequency=day&size=0&subreddit={}".format(typ, search, days, subreddit))

    if req.status_code != 200:
        raise APIError('Invalid Response Code by API. Got Status Code: ', req.status_code)

    raw_data = req.json()["aggs"]["created_utc"]

    dates = []
    counts = []
    for data in raw_data:
        utc = data["key"]
        dates.append(datetime.fromtimestamp(utc).date())
        counts.append(data["doc_count"])
    return [counts, dates]

def postFrequency(start=1594339200, end=1597017600, subreddit="animemes"):
    """
    Get frequency of posts and comments from start to end on a 24 hr interval
    @param: start : The start of time period in UNIX Timestamp
    @param: end : The end of time period in UNIX Timestamp
    @param: subreddit: The subreddit to search for
    """
    dates = []
    counts_posts = []
    counts_comments = []
    while start<end:
        posts,comments = getPostAndCommentCount(start)
        dates.append(datetime.fromtimestamp(start).date())
        counts_posts.append(posts)
        counts_comments.append(comments)
        print("Posts", posts, "on", datetime.fromtimestamp(start).day, "Comments", comments, "on", datetime.fromtimestamp(start).day)
        start+= 86400
        sleep(1)
    return [counts_posts, dates], [counts_comments, dates]

def plotCommentsQueries(queries):
    """
    Plots the Word count vs day on comments
    """
    # queries = ['trans','trap', 'tr*p', 'tr-', 'redacted']
    ax = plt.subplot(111)
    for query in queries:
        data = fetchDataReddit(query)
        print('Got Data for', query)
        plt.plot(data[1], data[0], label = query)
    plt.legend(frameon=False)
    plt.tick_params(top='off', right='off')
    plt.axvline(BAN_DATE, color='#f8381c')
    plt.ylabel('Comment Counts')
    plt.xlabel('Day')
    plt.title('Number of Comments containing different keywords on r/Animemes')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.show()

def plotPostQueries(queries):
    """
    Plots the word count vs days on posts
    """
    ax = plt.subplot(111)
    for query in queries:
        data = fetchDataReddit(query,"POSTS")
        print('Got Data for', query)
        plt.plot(data[1], data[0], label = query)
    plt.legend(frameon=False)
    plt.tick_params(top='off', right='off')
    plt.axvline(BAN_DATE, color='#f8381c')
    plt.ylabel('Keyword Counts')
    plt.xlabel('Day')
    plt.title('Number of Posts containing different keywords on r/Animemes')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.show()

def plotPostAndCommentFrequency(start):
    """
    Plot the Post Frequency 
    """
    posts , comments = postFrequency(start)
    ax = plt.subplot(111)

    plt.plot(comments[1], comments[0])
    plt.tick_params(top='off', right='off')
    plt.axvline(BAN_DATE, color='#f8381c')
    plt.ylabel('No. Of Comments')
    plt.xlabel('Day')
    plt.title('Daily comments on r/Animemes')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')
    plt.show()

    plt.plot(comments[1], comments[0])
    plt.tick_params(top='off', right='off')
    plt.axvline(BAN_DATE, color='#f8381c')
    plt.ylabel('No. Of Posts')
    plt.xlabel('Day')
    plt.title('Daily Posts on r/Animemes')
    plt.show()


def main():
    plotCommentsQueries(['trans','trap', 'tr*p', 'tr-', 'redacted'])
    plotPostQueries(['trans','trap', 'tr*p', 'tr-', 'redacted'])
    plotPostAndCommentFrequency(start=1594339200)

if if __name__ == "__main__":
    main()