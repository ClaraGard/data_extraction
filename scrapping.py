import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random

feed_selector = 'div[role = "feed"]'

def randomsleep(min, max):
    time.sleep(random.randint(min*1000, max*1000)/1000)

async def cookies(page):
    print("cookies")
    button_selector = '[data-cookiebanner = "accept_only_essential_button"]'
    if await page.query_selector(button_selector) == None:
        return False
    
    randomsleep(0, 2)
    await page.click(button_selector)
    return True

async def connect(page):
    print("connect")

    await cookies(page)
    mail_selector = '[id = "email"]'
    password_selector = '[id = "pass"]'
    button_selector = '[id = "loginbutton"]'
    if await page.query_selector(mail_selector) == None:
        return False
    
    await page.fill(mail_selector, 'dataextracproject2@gmail.com')
    randomsleep(0, 2)
    await page.fill(password_selector, 'DauphineIASD2!')
    randomsleep(0, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    return True

async def royal_connect(page):
    print("royal_connect")
    await cookies(page)
    mail_selector = '[data-testid = "royal_email"]'
    password_selector = '[data-testid = "royal_pass"]'
    button_selector = '[data-testid = "royal_login_button"]'
    if await page.query_selector(mail_selector) == None:
        return False
    
    await page.fill(mail_selector, 'dataextracproject2@gmail.com')
    randomsleep(0, 2)
    await page.fill(password_selector, 'DauphineIASD2!')
    randomsleep(0, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    return True

async def get_inner_text(element):
    inner_text = element.text_content()

    child_elements = element.query_selector_all('*')  # Get all child elements

    for child_element in child_elements:
        inner_text += get_inner_text(child_element)  # Recursively get innerText for each child

    return inner_text

async def get_author(page, i):
    post = feed_selector + f' > div:nth-child({i})'
    element = await page.query_selector(post)
    has_children = await element.query_selector('xpath=child::*')
    if not has_children:
        print(f"The element with selector '{feed_selector + f' > div:nth-child({i})'}'")
        for i in range(random.randint(0, 10)):
            await page.mouse.wheel(0, 500)
            randomsleep(0.1, 0.5)
    else:
        print(f"The element with selector '{feed_selector + f' > div:nth-child({i})'}' has children.")

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
    data = author_and_data.replace(author+" ", "", 1)
    print("author: ", author, "\ndata: ", data, "\nboth: ", author_and_data, sep="")
    return author, data

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False)
        page = await browser.new_page()

        await page.goto("https://www.facebook.com")
        await royal_connect(page)
        randomsleep(4, 6)
        if await connect(page):
            randomsleep(4, 6)

        # lis = await page.query_selector_all('li')
        # for li in lis:
        #     # Find <a> element inside the <li> with href containing "groups"
        #     a = await li.query_selector('a[href*=www.facebook.com/groups]')
        #     if a:
        #         # Click on the found <a> element
        #         await a.click()
        #         break

        # # css_selector = 'div[data-pagelet="LeftRail"] > div > div > div > ul li:nth-child(2) > div > a'
        # # await page.click(css_selector)
        # await page.wait_for_load_state('load')
        # await page.screenshot(path = "g.png")
        # print(await page.title())
        # await page.screenshot(path = "s.png")

        groups = pd.read_json('groups.json')['groups_names'].unique()
        columns = ['date',
                   'text',
                   'author',
                   'authordata',
                   'nbcomments',
                   'nbshares',
                   'nbreacts']
        dataset = pd.DataFrame(columns = columns)
        for group in groups:
            await page.goto(group)
            randomsleep(2, 4)
            if await royal_connect(page):
                randomsleep(2, 4)
            if await connect(page):
                randomsleep(2, 4)
            i = 2
            nb_old_posts = 0
            while nb_old_posts<15:
                author, author_data = await get_author(page, i)
                print(author, author_data)

                new_ligne = [None, None, author, author_data, None, None, None]
                dataset[len(dataset)] = new_ligne

                i += 1
                nb_old_posts += 1

        await browser.close()

asyncio.run(main())



