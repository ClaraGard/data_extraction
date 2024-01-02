import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time
import random

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
    
    await page.fill(mail_selector, 'dataextracproject@gmail.com')
    randomsleep(0, 2)
    await page.fill(password_selector, 'DauphineIASD1!')
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
    
    await page.fill(mail_selector, 'dataextracproject@gmail.com')
    randomsleep(0, 2)
    await page.fill(password_selector, 'DauphineIASD1!')
    randomsleep(0, 2)
    await page.click(button_selector)
    await page.wait_for_load_state('load')
    return True

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False)
        page = await browser.new_page()

        await page.goto("https://www.facebook.com")
        await royal_connect(page)
        randomsleep(4, 6)
        await connect(page)

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
        columns = ['title', 
                   'text',
                   'author']
        dataset = pd.DataFrame(columns = columns)
        for group in groups:
            print(group)
            await page.goto(group)
            randomsleep(2, 4)
            if await royal_connect(page):
                randomsleep(2, 4)
            if await connect(page):
                randomsleep(2, 4)
            await page.wait_for_load_state('load')
            randomsleep(2, 4)
            for _ in range(10):
                await page.mouse.wheel(0, 1000)
                randomsleep(1, 2)
            await page.screenshot(path = "group.png")



        await browser.close()

asyncio.run(main())