import pandas as pd
from datetime import datetime
import database
import ast

class Post():
    def __init__(self, date, content, author, author_data, comments, shares, reactions, images, links, group_link, link, scrapping_date):
        self.date = date
        self.content = content
        self.author = author
        self.author_data = author_data
        self.comments = comments
        self.shares = shares
        self.reactions = reactions
        self.images = images
        self.links = links
        self.group_link = group_link
        self.link = link
        self.scrapping_date = scrapping_date
    
    def get_csv_line(self):
        return [self.date, self.content, self.author, self.author_data, self.comments, self.shares, self.reactions, self.images, self.links, self.group_link, self.link, self.scrapping_date]

dataset = pd.read_csv("dataset.csv")
session = database.get_session()
for i in range(len(dataset)):
    line = dataset.loc[i]
    datetime_object = datetime.strptime(line["date"], '%Y-%m-%d %H:%M:%S')
    links_list = ast.literal_eval(line["links"])
    links_list = [i for i in links_list if i is not None]
    images_list = ast.literal_eval(line["images"])
    images_list = [i for i in images_list if i is not None]
    post = Post(datetime_object, line["text"], line["author"], line["authordata"], int(line["nbcomments"]), int(line["nbshares"]), int(line["nbreacts"]), images_list,
                 links_list, line["group"], line["link"], datetime(year=2024, month=1, day=5))
    database.insert_post(post, session)

database.close_session(session)
