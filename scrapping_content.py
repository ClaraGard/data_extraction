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

import regex as re

async def get_content(selector, page):
    inner_text = await page.locator(selector).text_content()

    # We may need to click on "En voir plus"
    if re.search("oir plus", inner_text[-20:]):
        button_selector = selector \
                           + ' > div'*4 \
                           + ' > span' \
                           + ' > div:last-child' \
                           + ' > div' \
                           + ' > div[role = "button"]'
        await page.wait_for_selector(button_selector)
        await page.click(button_selector)
        print('yeah')

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
        print("no see more")
        result = None
        
    # Case where the post is a text in an image.
    if not result:
        content_selector = selector \
                           + ' > div'*3 \
                           + ' > div:nth-child(2)' \
                           + ' > div'*2     
        if await page.query_selector(content_selector) is not None:
            print("texte à image")
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
            print("no images here")
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
        print('one image')
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
            print('several images')
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
            for image in images['img']:
                result['textContent'] += ' ' + image
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
    
    print("yyyyyyyyyyyyyyyy", result['textContent'] )
    print(result['emojis'], images['img'], result['links'], '\n\n')

    return result['textContent'] 

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
        columns = ['date',
                   'text',
                   'author',
                   'nbcomments',
                   'nbshares',
                   'nbreacts']
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
            # for _ in range(10):
            #     await page.mouse.wheel(0, 1000)
            #     randomsleep(1, 2)
            await page.screenshot(path = "group.png")
            feed_selector = 'div[role = "feed"]'
            nb_of_posts = await page.query_selector(feed_selector)
            nb_of_posts = await nb_of_posts.query_selector_all('xpath=child::*')
            print(len(nb_of_posts))
            for i in range(2, 50):
            # for i in range(2, len(nb_of_posts) + 1):
                post = feed_selector + f' > div:nth-child({i})'
                element = await page.query_selector(post)
                has_children = await element.query_selector('xpath=child::*')
                if not has_children:
                    print(f"The element with selector '{feed_selector + f' > div:nth-child({i})'}'")
                    # for _ in range(10):
                    await page.mouse.wheel(0, 2000)
                    randomsleep(1, 2) 
                else:
                    print(f"The element with selector '{feed_selector + f' > div:nth-child({i})'}' has children.")
                      
                author_selector = feed_selector \
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
                                  + ' > span'*2 \
                                  + ' > a' \
                                  + ' > strong' \
                                  + ' > span'
                # print(author_selector)
                # await page.wait_for_load_state('load')  
                # await page.wait_for_selector(author_selector, timeout = 20000, state = 'hidden')
                try:
                    author = await page.locator(author_selector).text_content()
                except:
                    author_selector = feed_selector \
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
                                      + ' > div'*2 \
                                      + ' > strong' \
                                      + ' > object' \
                                      + ' > div' 
                    author = await page.locator(author_selector).text_content()
                print(author)

                content_selector = feed_selector \
                                   + f' > div:nth-child({i})' \
                                   + ' > div'*9 \
                                   + ' > div:nth-child(2)' \
                                   + ' > div'*2 \
                                   + ' > div:nth-child(3)'
                # print(content_selector)
                try:
                    content = await get_content(content_selector, page)
                except:
                    content = 0
                # print(content)
                new_ligne = [None, None, author, None, None, None]
                # dataset = dataset.append(pd.Series(new_ligne, index = dataset.columns), ignore_index = True)

        await browser.close()

asyncio.run(main())



