# What is this?
Basically, this is a tool which allow you to collect emails from Facebook fanpages or posts comments.
# How to use?
1. **make a Facebook app** and get the **App's ID and Secret key**.
2. Place them in **FB_ACCESS_TOKEN** variable (line 16, `MailScraper.py`) like this:

   > FB_ACCESS_TOKEN = "APP_ID|APP_SECRET"

3. Change the configs in `run.py`. 

Configs | Description
------------ | -------------
input_data | Facebook post id or page username/id
mode | 0: extract email from a post, 1: extract email from posts from a fanpage
post_limit | number of posts you want to extract email from. set to 0 to get all
comment_limit | number of comments you want to extract email from. set to 0 to get all
csv | export in csv format

That's it! Have fun using it!