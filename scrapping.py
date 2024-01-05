import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random
import regex as re
from datetime import datetime, timedelta
from config import Config

feed_selector = 'div[role = "feed"]'
config_json = pd.read_json('config.json')
account = Config.Account(config_json["account"]["email"], config_json["account"]["password"])
date = Config.Date(config_json["date"]["years"], config_json["date"]["months"], config_json["date"]["weeks"], config_json["date"]["days"], config_json["date"]["hours"], config_json["date"]["minutes"], config_json["date"]["months of the year"])
multipliers = Config.Multipliers(config_json["multipliers"]["thousands"], config_json["multipliers"]["millions"], config_json["multipliers"]["millions"])
timings = Config.Timings(config_json["timings"]["time to load page"], config_json["multipliers"]["timeout"])
misc = Config.Misc(config_json["misc"]["see more"], config_json["misc"]["know more"])
config = Config(account, date, multipliers, timings, misc)

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
    await page.fill(mail_selector, config.account.email)
    randomsleep(1.5, 4)
    await page.fill(password_selector, config.account.password)
    randomsleep(1, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    randomsleep(config.timings.time_to_load, config.timings.time_to_load+2)
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
    await page.fill(mail_selector, config.account.email)
    randomsleep(1.5, 4)
    await page.fill(password_selector, config.account.password)
    randomsleep(1, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    randomsleep(config.timings.time_to_load, config.timings.time_to_load+2)
    return True

async def is_short_video(page, i):
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)
    
    short_video_selector = feed_selector \
                + f' > div:nth-child({i})' \
                + ' > div'*9 \
                + ' > div:nth-child(2)' \
                + ' > div'*2 \
                + ' > div:nth-child(2)' \
                + ' > div'*3 \
                + ' > a' \
                + ' > div'*2
    
    element = await page.query_selector(short_video_selector)
    if element is None:
        return False
    reel = await element.get_attribute('data-pagelet')
    return reel == "Reels"

async def get_author(page, i):
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)

    author_and_data_selector = feed_selector \
                    + f' > div:nth-child({i})' \
                    + ' > div'*9 \
                    + ' > div:nth-child(2)' \
                    + ' > div'*2 \
                    + ' > div:nth-child(2)' \
                    + ' > div' \
                    + ' > div:nth-child(2)' \
                    + ' > div'*2 \
                    + ' > span' \
                    + ' > h3' \
                    + ' > span' \
    
    author_and_data = await page.locator(author_and_data_selector).text_content()
    author_selector = await page.query_selector(author_and_data_selector)
    author_selector = await author_selector.query_selector_all('xpath=child::*')
    author = ''
    for s in author_selector:
        text = await s.text_content()
        if text:
            author = text
            break
    if author == author_and_data:
        data = ""
    else:
        data = author_and_data.replace(author+" ", "", 1)
    return author, data

async def get_link(page, i):
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)

    link_selector = feed_selector \
                    + f' > div:nth-child({i})' \
                    + ' > div'*9 \
                    + ' > div:nth-child(2)' \
                    + ' > div'*2 \
                    + ' > div:nth-child(2)' \
                    + ' > div' \
                    + ' > div:nth-child(2)' \
                    + ' > div' \
                    + ' > div:nth-child(2)' \
                    + ' > span' *2\
                    + ' > span:nth-child(2)' \
                    + ' > span' \
                    + ' > a' \
    
    element = await page.query_selector(link_selector)
    if element is None:
        raise Exception("Couldn't get link"+link_selector)
    link = await element.get_attribute('href')
    return link

async def get_date(page, i):
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)

    date_selector = feed_selector \
                    + f' > div:nth-child({i})' \
                    + ' > div'*9 \
                    + ' > div:nth-child(2)' \
                    + ' > div'*2 \
                    + ' > div:nth-child(2)' \
                    + ' > div' \
                    + ' > div:nth-child(2)' \
                    + ' > div' \
                    + ' > div:nth-child(2)' \
                    + ' > span' *2\
                    + ' > span:nth-child(2)' \
                    + ' > span' \
                    + ' > a' \
    
    date_string = await page.locator(date_selector).text_content()
    numbers = list(map(int, re.findall(r'\d+', date_string)))
    date = datetime.now()
    if len(numbers) > 1:
        for i in range(len(config.date.months_of_the_year)):
            if config.date.months_of_the_year[i] in date_string:
                date = datetime(year=numbers[1], day=numbers[0], month=i)
                break
            if i == 11:
                raise Exception("Date format unrecognized "+date_string)
    
    elif config.date.years in date_string:
        date -= timedelta(days=365*numbers[0])
    elif config.date.months in date_string:
        date -= timedelta(days=30*numbers[0])
    elif config.date.weeks in date_string:
        date -= timedelta(days=7*numbers[0])
    elif config.date.days in date_string:
        date -= timedelta(days=numbers[0])
    elif config.date.hours in date_string:
        date -= timedelta(hours=numbers[0])
    elif config.date.minutes in date_string:
        date -= timedelta(minutes=numbers[0])
    else:
        raise Exception("Date format unrecognized "+date_string)
    date = date.replace(second=0, microsecond=0)
    return date

async def get_data(page, i):
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)

    data_selector = feed_selector \
                    + f' > div:nth-child({i})' \
                    + ' > div'*9 \
                    + ' > div:nth-child(2)' \
                    + ' > div'*2 \
                    + ' > div:nth-child(4)' \
                    + ' > div'*6 
    
    reactions_selector = data_selector + ' > div'*2 \
                    + ' > span' \
                    + ' > div' \
                    + ' > span:nth-child(2)' \
                    + ' > span'*2 
                    
    if await page.query_selector(reactions_selector) is not None:
        reactions = await page.locator(reactions_selector).text_content()
        reactions = reactions.split()
        if len(reactions) == 1:
            m = 1
        elif reactions[1] == config.multipliers.thousands:
            m = 1000
        elif reactions[1] == config.multipliers.millions:
            m = 1000000
        elif reactions[1] == config.multipliers.billions:
            m = 1000000000
        else:
            m = 1
        reactions = int(float(reactions[0].replace(",","."))*m)
    else:
        reactions = 0
    
    comments_selector = data_selector + ' > div:nth-child(2)' \
                    + ' > div:nth-child(2)' \
                    + ' > span' \
                    + ' > div' \
                    + ' > span' 
    
    if await page.query_selector(comments_selector) is not None:   
        comments = await page.locator(comments_selector).text_content()
        comments = comments.split()
        if len(comments) == 1:
            m = 1
        elif comments[1] == config.multipliers.thousands:
            m = 1000
        elif comments[1] == config.multipliers.millions:
            m = 1000000
        elif comments[1] == config.multipliers.billions:
            m = 1000000000
        else:
            m = 1
        comments = int(float(comments[0].replace(",","."))*m)
    else:
        comments = 0

    shares_selector = data_selector + ' > div:nth-child(2)' \
                    + ' > div:nth-child(3)' \
                    + ' > span' \
                    + ' > div' \
                    + ' > span' 
    
    if await page.query_selector(shares_selector) is not None:   
        shares = await page.locator(shares_selector).text_content()
        shares = shares.split()
        if len(shares) == 1:
            m = 1
        elif shares[1] == config.multipliers.thousands:
            m = 1000
        elif shares[1] == config.multipliers.millions:
            m = 1000000
        elif shares[1] == config.multipliers.billions:
            m = 1000000000
        else:
            m = 1
        shares = int(float(shares[0].replace(",","."))*m)
    else:
        shares = 0

    return reactions, comments, shares

async def get_content(page, i):
    selector = feed_selector \
                                   + f' > div:nth-child({i})' \
                                   + ' > div'*9 \
                                   + ' > div:nth-child(2)' \
                                   + ' > div'*2 \
                                   + ' > div:nth-child(3)'
    element = await page.query_selector(selector)

    inner_text = await page.locator(selector).text_content()

    # We may need to click on "En voir plus"
    if re.search(config.misc.see_more, inner_text[-20:], re.IGNORECASE) and re.search(config.misc.know_more, inner_text[-20:], re.IGNORECASE) is None:
        button_selector = selector \
                           + ' > div'*4 \
                           + ' > span' \
                           + ' > div:last-child' \
                           + ' > div' \
                           + ' > div[role = "button"]'
        await page.wait_for_selector(button_selector)
        await page.click(button_selector)
        #print('yeah')

    # We want to extract the text content of the post (with emojis)
    # Regular text
    content_selector = selector \
                       + ' > div'*4 \
                       + ' > span' \
                       + ' > div'*2
    if await page.query_selector(content_selector) is None:
        # Smaller text
        content_selector = selector \
                       + ' > div'*4
    if await page.query_selector(content_selector) is not None:
        result = await page.evaluate('''(selector) => {
                const elements = document.querySelectorAll(selector);
                if (!elements) return null;
                const data = {
                    textContent: "",
                    emojis: [],
                    links: [],
                    is_image: false,
                };
                elements.forEach(element => {
                    data.textContent += element.textContent.trim() + ' ';
                    const children = element.children;
                    for (const child of children) {
                        if (child && child.tagName === 'SPAN') {
                            const imgChild = child.firstElementChild;
                            if (imgChild && imgChild.tagName === 'IMG' && imgChild.hasAttribute('alt')) {
                                data.textContent += imgChild.getAttribute('alt') + ' ';
                                data.emojis.push(imgChild.getAttribute('alt'));
                            } if (imgChild && imgChild.tagName === 'A' && imgChild.hasAttribute('href')) {
                                data.links.push(imgChild.getAttribute('href'));
                            }
                        }
                    }
                });
                return data;
            }''', content_selector)
    else:
        #print("no see more")
        result = None
        
    # Case where the post is a text in an image.
    if not result:
        content_selector = selector \
                           + ' > div'*3 \
                           + ' > div:nth-child(2)' \
                           + ' > div'*2     
        if await page.query_selector(content_selector) is not None:
            #print("texte à image")
            result = await page.evaluate('''(selector) => {
                    const elements = document.querySelectorAll(selector);
                    if (!elements) return null;
                    const data = {
                        textContent: "",
                        emojis: [],
                        links: [],
                        is_image: true,
                    };
                    elements.forEach(element => {
                        data.textContent += element.textContent.trim() + ' ';
                        const children = element.children;
                        for (const child of children) {
                            if (child && child.tagName === 'SPAN') {
                                const imgChild = child.firstElementChild;
                                if (imgChild && imgChild.tagName === 'IMG' && imgChild.hasAttribute('alt')) {
                                    data.textContent += imgChild.getAttribute('alt') + ' ';
                                    data.emojis.push(imgChild.getAttribute('alt'));
                                }
                            }
                        }
                    });
                    return data;
                }''', content_selector)
        else:
            #print("no images here")
            result = {'textContent': "", 'emojis': [], 'links': [], 'is_image': False}

    # We want to include images inside the text.
    if result['textContent'] == "":
        which_div = ' > div'
    else:
        which_div = ' > div:nth-child(2)'
    # one image
    images_selector = selector \
                          + which_div \
                          + ' > div' \
                          + ' > a' \
                          + ' > div'*4 \
                          + ' > img'
    root = await page.query_selector(images_selector)
    if root is not None:
        #print('one image')
        images = {'img': []}
        attribute_value = await root.get_attribute('src')
        images['img'].append(attribute_value)
        for image in images['img']:
            result['textContent'] += ' ' + image
    else:
        # several images
        images_selector = selector \
                          + which_div \
                          + ' > div'*5 \
                          + ' > a' \
                          + ' > div'*3
        root = await page.query_selector(images_selector)
        if root is not None:
            #print('several images')
            images_selector = selector \
                          + which_div \
                          + ' > div'*4
            root = await page.query_selector(images_selector)
            descendants = await root.query_selector_all('xpath=child::*')
            images = {'img': []}
            for descendant in descendants:
                aChild = await descendant.query_selector_all('xpath=child::*')
                divChild = await aChild[0].query_selector_all('xpath=child::*')
                divChild2 = await divChild[0].query_selector_all('xpath=child::*')
                divChild3 = await divChild2[0].query_selector_all('xpath=child::*')
                imgChild = await divChild3[0].query_selector_all('xpath=child::*')
                attribute_value = await imgChild[0].get_attribute('src')
                images['img'].append(attribute_value)
        else:
            images = {'img': []}

    # link_to_other_post_selector = selector \
    #                       + which_div \
    #                       + ' > div'
    # if await page.query_selector(link_to_other_post_selector) is not None:
    #     other_post = await page.evaluate('''(selector) => {
    #             const element = document.querySelector(selector);
    #             if (!element) return null;
    #             const descendants = element.querySelectorAll('*');
    #             const data = {
    #                 citations: [],
    #             };
    #             descendants.forEach(descendant => {
    #                 if (descendant.tagName === 'A' && descendant.hasAttribute('href') && descendant.hasAttribute('waprocessedanchor') == true) {
    #                     data.citations.push(descendant.getAttribute('href'));
    #                 } 
    #             });
    #             return data;
    #         }''', link_to_other_post_selector)
    #     print("other post done !!!")
    #     for cite in other_post['citations']:
    #         result['textContent'] += ' ' + cite
    #         result['cite_other_post'] = True
    # else:
    #     result['cite_other_post'] = False
    
    #print("yyyyyyyyyyyyyyyy", result['textContent'] )
    #print(result['emojis'], images['img'], result['links'], '\n\n')
    return result['textContent'], result['links'], images['img']
                    
    

async def main():
    groups = pd.read_json('groups.json')['groups_names'].unique()
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
               'link']
    dataset = pd.DataFrame(columns = columns)

    start = datetime.now()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False)
        page = await browser.new_page()
        await page.evaluate('''() => {return document.documentElement.requestFullscreen();}''')
        await page.set_viewport_size({'width': 1920, 'height': 1080})

        page.set_default_timeout(10*3600*1000)

        await page.goto("https://www.facebook.com")
        await royal_connect(page)
        await connect(page)

        for group in groups:
            await page.goto(group)
            randomsleep(config.timings.time_to_load, config.timings.time_to_load+2)
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

                if await is_short_video(page, i):
                    print("short video")
                    continue
                author, author_data = await get_author(page, i)
                print("author:", author, author_data)
                reactions, comments, shares = await get_data(page, i)
                print("reactions:", reactions, "comments:", comments, "shares:", shares)
                date = await get_date(page, i)
                if is_old(date):
                    nb_old_posts += 1
                else:
                    nb_old_posts = 0
                print("approximated date:", date.strftime("%Y-%m-%d %H:%M:%S"))
                link = await get_link(page, i)
                print(link)
                content, links, images = await get_content(page, i)
                print("content:",content)
                print("links:", links)
                print("images:", images)
                new_ligne = [date, content, author, author_data, comments, shares, reactions, images, links, group, link]
                dataset.loc[len(dataset)] = new_ligne
                print("")
        await browser.close()
        dataset.to_csv("dataset.csv")
        end = datetime.now()
        print(str(end-start))

asyncio.run(main())



