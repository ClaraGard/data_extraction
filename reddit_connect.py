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

feed_selector = '[id="2x-container"] > div > div:nth-child(2) > div:nth-child(4) > div > div > div > div:nth-child(2) > div:nth-child(5) > div > div:nth-child(5)'

def randomsleep(min, max):
    time.sleep(random.randint(min*1000, max*1000)/1000)

async def cookies(page):
    print("cookies")
    cookies_button = '[id=reject-nonessential-cookies-button]'
    if await page.query_selector(cookies_button) == None:
        return False
    await page.click(cookies_button)
    randomsleep(1.5, 4)
    print("cookies succeed")
    return True


async def connect(page):
    print("connect")
    connect_button1 = 'faceplate-tracker[noun="login"]'
    username_input = '[id="login-username"]'
    password_input = '[id="login-password"]'
    connect_button2 = 'faceplate-tracker[source="onboarding"][action="click"][noun="login"]'
    if await page.query_selector(connect_button1) == None:
        return False
    
    await page.click(connect_button1)
    randomsleep(1.5, 4)
    await page.fill(username_input, config.config.account.username)
    randomsleep(1.5, 4)
    await page.fill(password_input, config.config.account.password)
    randomsleep(1, 2)
    await page.click(connect_button2)
    await page.wait_for_load_state('load')
    randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
    print("connect succeed")
    return True

async def click_post(page, i):
    print("click post ", i)
    post_selector = feed_selector + f' > div:nth-child({i+1})'
    if await page.query_selector(post_selector) == None:
        return False
    await page.click(post_selector)
    randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
    print("click post ", i, "succeed")
    return True

async def backwards(page):
    print("go back")
    await page.go_back()
    randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
    print("go back succeed")

async def feed_exists(page):
    return await page.query_selector(feed_selector) is not None

async def main():
    start = datetime.now()
    async with async_playwright() as p:
        headless = False
        browser = await p.chromium.launch(headless = headless)
        page = await browser.new_page()
        page.set_default_timeout(config.config.timings.timeout*1000)
        if not headless:
            await page.evaluate('''() => {return document.documentElement.requestFullscreen();}''')
            await page.set_viewport_size({'width': 1920, 'height': 1080})

        await page.goto("https://www.reddit.com")
        randomsleep(3, 5)
        await cookies(page)
        await connect(page)
        subreddits = pd.read_json('subreddits.json')['subreddits'].unique()
        for subreddit in subreddits:
            await page.goto(subreddit)
            randomsleep(config.config.timings.time_to_load, config.config.timings.time_to_load+2)
            await click_post(page, 2)
            



asyncio.run(main())

