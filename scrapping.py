import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless = False)
        page = await browser.new_page()

        # await page.goto("http://www.facebook.com")

        # button_selector = '[data-cookiebanner = "accept_only_essential_button"]'
        # await page.click(button_selector)

        # input_selector = '[data-testid = "royal_email"]'
        # await page.fill(input_selector, 'dataextracproject@gmail.com')
            
        # input_selector = '[data-testid = "royal_pass"]'
        # await page.fill(input_selector, 'DauphineIASD1!')

        # button_selector = '[data-testid = "royal_login_button"]'
        # await page.click(button_selector)
        # await page.wait_for_load_state('load')

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
            await page.goto(group)
            await page.wait_for_load_state('load')
            time.sleep(4)
            await page.screenshot(path = "group.png")



        await browser.close()

asyncio.run(main())