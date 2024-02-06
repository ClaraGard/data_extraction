feed_selector = 'div[role = "feed"]'

short_video_selector = feed_selector \
                + f' > div:nth-child({2})' \
                + ' > div'*9 \
                + ' > div:nth-child(2)' \
                + ' > div'*2 \
                + ' > div:nth-child(2)' \
                + ' > div'*3 \
                + ' > a' \
                + ' > div'*2

print(short_video_selector)