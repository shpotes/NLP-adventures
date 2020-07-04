#!/usr/bin/env python3

import re
from xml.etree import ElementTree as ET
import requests
import bs4

class Comment:
    def __init__(self, raw):
        self.content = self.compute_content(raw.find('p'))
        karma = raw.find('div', attrs={'class': 'comment_feedback'})
        self.id = re.search(r'#\d+',
                            raw.find('div', attrs={'class': 'userinfo'}).text).group(0)

        votes = raw.find('span', attrs={'class': 'comment_votes'})
        self.votes = int(votes.text)
        self.votes *= -1 if votes['class'][1] == 'negative' else 1
        self.total_votes = int(re.search(r'\d+',
                                        karma.findAll('small')[-1].text.strip()
                                       ).group(0))

    def to_xml(self):
        return

    def compute_content(self, raw):
        childs = list(raw.children)
        idx = 0
        for i, child in enumerate(childs):

            if hasattr(child, 'text') and re.match(r'#\d+\s+\w+ dijo:', child.text):
                idx = i
                break

        return ' '.join(filter(lambda x: isinstance(x, str), childs[idx:])).strip()

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content

    
class ADV:
    def __init__(self, raw: bs4.element.Tag):
        comments = raw.find('div', attrs={'class': 'comment_tag'}).find('a')
        meta = raw.find('div', attrs={'class': 'pre'})
        metrics = raw.find('div', attrs={'class': 'meta'}).findAll('span')

        self.content = raw.find('p', attrs={'class': 'story_content storyTitle'}).find('a').contents[0]

        self.n_comments = int(comments.text)
        self.comments_url = comments['href'].split('#')[0]

        self.date = re.search(r'\d [A-Z][a-z]+ \d{4}', meta.text.strip()).group(0) # TODO: parse this shit
        self.category = meta.find('a').contents[0]

        self.metrics = dict(map(lambda x: (x.contents[0].contents[0],
                                           int(re.sub('\D','', x.contents[1]))),
                                metrics))

    def get_comments(self):
        rc = requests.get(self.comments_url)
        comment_soup = bs4.BeautifulSoup(rc.content, 'html5lib')
        comments = comment_soup.findAll('div', attrs={'class': 'comment_box'})

        return [Comment(comment) for comment in comments]

    def __str__(self):
        return self.content

    def __repr__(self):
        return self.content


def load(url='https://www.ascodevida.com/'):
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, 'html5lib')

    main_page = soup.find('div', attrs={'id': 'main'})
    posts = main_page.findAll('div', attrs={'class': 'box story'})

    adv = [ADV(post) for post in posts]
    return adv
