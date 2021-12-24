import re
import sys

def word2age(w):
    ranges = {'teens':18,'twenties':25,'thirties':35,'forties':45,'fifties':55}
    if w[:3].lower() == 'mid':
        w = w[3:]
    if w in ranges:
        return ranges[w]


def isint(w):
    return str(int(w)) == w


def get_blog_info(client, blogName):
    info = client.blog_info(blogName)
    return info


def get_blog_age(client, blogName):
    info = get_blog_info(client, blogName)
    # check title first
    title = info['title']
    title = re.sub('[^0-9a-zA-Z\+\-\']+', ' ', title)
    for w in title.split():
        if len(w) == 2 and isint(w):
            return int(w)
    desc = info['description']
    # check description for a 2-digit number specifically set off by commas (most likely age format)
    for w in desc.split(','):
        w = w.strip()
        if len(w) == 2 and isint(w):
            return int(w)
    # otherwise, look for any 2-digit numbers in description
    # strip non-alphanumeric (ok to strip unicode, we're only looking for numbers)
    # but leave dash (for long-form numbers) and plus (for '18+')
    desc = re.sub('[^0-9a-zA-Z\+\-\']+', ' ', desc)
    nums = []
    for w in desc.split():
        if len(w) == 2 and isint(w):
            nums.append(int(w))
    if len(nums) == 0:
        return None
    if len(nums) == 1:
        return nums[0]
    # TODO: if len(nums)>1, select most likely number as age?
    # check for like... '18 or older', 'you need to be 18' etc. or references to 'the fifties', etc.
    return nums[0]


def get_reblog_arrows(client, blogName):
    # get list of blogs this blog reblogs from
    posts = []
    # get 5 batches of 20 posts
    for i in range(5):
        posts += client.posts(blogName, offset=i*20, limit=20, reblog_info=True)
    sources = defaultdict(int)
    for post in posts:
        # TODO: get who the post was reblogged from
        sourcename = None
        sources[sourcename] += 1
    return sources


def get_follow_arrows(client, blogName):
    # get the list of blogs this blog follows (when available)
    follows = client.blog_following(blogName)
    sources = {}
    if len(follows['users']) == 0:
        return sources
    for blog in follows['users']:
        sources[blog['name']] = 1
    return sources


def walk_reblog_graph(client, blogName, depth=0, limit=10):
    # start to walk the graph from the root at rootName
    # TODO
    graph = {}
    sources = get_reblog_arrows(client, blogName)
    graph[blogName] = list(sources.keys())
    if depth > limit:
        return graph
    for sourceName in sources:
        subgraph = get_reblog_arrows(client, sourceName, depth=depth+1, limit=limit)
        for name in subgraph:
            graph[name] = subgraph[name]
    return graph
