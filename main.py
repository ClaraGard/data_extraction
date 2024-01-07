import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random
import regex as re
from datetime import datetime, timedelta
import config
import scrapping
import database

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
        l = [self.date, self.content, self.author, self.author_data, self.comments, self.shares, self.reactions, self.images, self.links, self.group_link, self.link, self.scrapping_date]
        return [str(i) for i in l]



feed_selector = 'div[role = "feed"]'

def is_old(date):
    return datetime.now() - date >= timedelta(days=2, minutes=1)

def randomsleep(min, max):
    time.sleep(random.randint(min*1000, max*1000)/1000)

async def randomscroll(page, min, max):
    scrolls = random.randint(min, max)
    print("scrolling", scrolls, "times")
    for _ in range(scrolls):
        await page.mouse.wheel(0, 700)
        randomsleep(0.05, 0.6)
    
async def scroll_if_needed(element, page):
    has_children = await element.query_selector('xpath=child::*')
    if not has_children:
        await randomscroll(page, 5, 10)
        randomsleep(1.5, 3)

async def scroll_into_view(page, i):
    print("scrolling...")
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)
    await element.evaluate("element => element.scrollIntoViewIfNeeded()")
    randomsleep(0.5, 1.5)
    print("done scrolling")

async def cookies(page):
    print("cookies")
    button_selector = '[data-cookiebanner = "accept_only_essential_button"]'
    if await page.query_selector(button_selector) == None:
        return False
    await page.click(button_selector)
    randomsleep(0.5, 2.5)
    return True

async def connect(page):
    print("connect")
    await cookies(page)
    mail_selector = '[id = "email"]'
    password_selector = '[id = "pass"]'
    button_selector = '[id = "loginbutton"]'
    if await page.query_selector(mail_selector) == None:
        return False
    
    randomsleep(1.5, 4)
    await page.fill(mail_selector, config.config.account.email)
    randomsleep(1.5, 4)
    await page.fill(password_selector, config.config.account.password)
    randomsleep(1, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
    return True

async def royal_connect(page):
    print("royal_connect")
    await cookies(page)
    mail_selector = '[data-testid = "royal_email"]'
    password_selector = '[data-testid = "royal_pass"]'
    button_selector = '[data-testid = "royal_login_button"]'
    if await page.query_selector(mail_selector) == None:
        return False
    
    randomsleep(1.5, 4)
    await page.fill(mail_selector, config.config.account.email)
    randomsleep(1.5, 4)
    await page.fill(password_selector, config.config.account.password)
    randomsleep(1, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
    return True

async def scrappe(page, i, group):
    try: 
        short_video = await scrapping.is_short_video(page, i)
    except:
        short_video = False
    if short_video:
        print("short video")
        return
    
    author_task = asyncio.create_task(scrapping.get_author(page, i))
    reactions_task = asyncio.create_task(scrapping.get_reactions(page, i))
    comments_task = asyncio.create_task(scrapping.get_comments(page, i))
    shares_task = asyncio.create_task(scrapping.get_shares(page, i))
    date_task = asyncio.create_task(scrapping.get_date(page, i))
    link_task = asyncio.create_task(scrapping.get_link(page, i))
    content_task = asyncio.create_task(scrapping.get_content(page, i))
    

    try:
        author = await author_task
    except Exception as e:
        author = ["#Error couldn't scrappe: " + str(e)]*2
    print("author:", author)


    try:
        reactions = await reactions_task
    except Exception as e:
        reactions = "#Error couldn't scrappe: " + str(e)
    print("reactions:", reactions)

    try:
        comments = await comments_task
    except Exception as e:
        comments = "#Error couldn't scrappe: " + str(e)
    print("comments:", comments)

    try:
        shares = await shares_task
    except Exception as e:
        shares = "#Error couldn't scrappe: " + str(e)
    print("shares:", shares)


    try:
        date = await date_task
    except Exception as e:
        date = datetime.min
    print("approximated date:", date.strftime("%Y-%m-%d %H:%M:%S"))


    try:
        link = await link_task
    except Exception as e:
        link = "#Error couldn't scrappe: " + str(e)
    print(link)


    try:
        content_links_images = await content_task
    except Exception as e:
        content_links_images = ["#Error couldn't scrappe: " + str(e)]*3
    print("content:",content_links_images[0])
    print("links:", content_links_images[1])
    print("images:", content_links_images[2])


    post = Post(date, content_links_images[0], author[0], author[1], comments, shares, reactions, content_links_images[2], content_links_images[1], group, link, datetime.now())
    return post

async def main():
    groups = pd.read_json('groups.json')['groups_names'].unique()
    session = database.get_session()
    if config.config.files.input == "":
        columns = ['date',
                'text',
                'author',
                'authordata',
                'nbcomments',
                'nbshares',
                'nbreacts',
                'images',
                'links',
                'group',
                'link',
                'scrappingdate']
        dataset = pd.DataFrame(columns = columns)
    else:
        dataset = pd.read_csv(config.config.files.input)

    start = datetime.now()
    async with async_playwright() as p:
        headless = True
        browser = await p.chromium.launch(headless = headless)
        page = await browser.new_page()
        page.set_default_timeout(config.config.timings.timeout*1000)
        if not headless:
            await page.evaluate('''() => {return document.documentElement.requestFullscreen();}''')
            await page.set_viewport_size({'width': 1920, 'height': 1080})

        #page.set_default_timeout(10*3600*1000)

        await page.goto("https://www.facebook.com")
        await royal_connect(page)
        await connect(page)

        for group in groups:
            await page.goto(group)
            randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
            print("\n---------------\n")
            print(group)

            await royal_connect(page)
            await connect(page)

            i = 1
            nb_old_posts = 0
            while nb_old_posts<20:
                i += 1
                print("post:", i-1, " |  consecutive old posts:", nb_old_posts)
                await scroll_into_view(page, i)
                post = await scrappe(page, i, group)
                if post is None:
                    continue

                if is_old(post.date):
                    nb_old_posts += 1
                else:
                    nb_old_posts = 0
                print(dataset)
                print(post.get_csv_line())
                dataset.loc[len(dataset)] = post.get_csv_line()
                print("")
                database.insert_post(post, session)
            dataset.to_csv(config.config.files.output, index=False)
        await browser.close()
        end = datetime.now()
        print("Scrapping finished, scrapped", len(groups), "groups and", len(dataset), "posts in", str(end-start))

asyncio.run(main())



