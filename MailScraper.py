#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
import requests 
import re
from pathlib import Path
from datetime import datetime

class FCEE:
    """
        Facebook Comments Email Extractor 
    """
    
    # GLOBAL VARS
    FB_ACCESS_TOKEN  = ''
    API_GET_COMMENTS = 'https://graph.facebook.com/v3.0/{0}/comments?limit={1}&after={2}&access_token=' + FB_ACCESS_TOKEN
    API_GET_POSTS    = 'https://graph.facebook.com/v3.0/{0}/posts?limit={1}&after={2}&access_token=' + FB_ACCESS_TOKEN
    LOG_FILE_NAME    = 'log.txt'
    SUCCESS_RESPONSE_CODE = 200
    ERROR_RESPONSE_CODE   = 400

    def __init__(self, input_data, mode = 0, post_limit = 10, comment_limit = 50, csv = False):
        self.mode = mode
        #csv formatted
        self.csv = csv
        #number of posts to extract from, 0 = get all
        self.post_limit = post_limit
        if post_limit == 0: 
            self.get_all_posts = True
            self.post_limit = 50
        else: 
            self.get_all_posts = False

        #number of posts to extract from, 0 = get all
        self.comment_limit = comment_limit
        if comment_limit == 0: 
            self.get_all_comments = True
            self.comment_limit = 500
        else: 
            self.get_all_comments = False

        #log file header
        self.intro = """
        $$$$$$$$\  $$$$$$\  $$$$$$$$\ $$$$$$$$\ 
        $$  _____|$$  __$$\ $$  _____|$$  _____|
        $$ |      $$ /  \__|$$ |      $$ |      
        $$$$$\    $$ |      $$$$$\    $$$$$\    
        $$  __|   $$ |      $$  __|   $$  __|   
        $$ |      $$ |  $$\ $$ |      $$ |      
        $$ |      \$$$$$$  |$$$$$$$$\ $$$$$$$$\ 
        \__|       \______/ \________|\________|
        Facebook Comments Email Extractor 
        Launched at: {0}
        Configs: 
                + input: "{1}"
                + mode: {2}
                + post_limit: {3}
                + comment_limit: {4}
                + csv: {5}
        -----------------------------------------                                
        """.format(datetime.now(), input_data, mode, post_limit, comment_limit, csv)
        print(self.intro)
        
        #mode = 0 for extracting comments from a single post
        #mode = 1 for extracting posts from a fanpage
        if mode == 0:
            self.indentifier = input_data
            self.dump_comments(input_data)
        elif mode == 1:
            self.indentifier = input_data
            self.extracted_posts = self.get_extracted_posts(self.indentifier)
            self.dump_posts(input_data)

    def http_request(self, url):
        #requesting reponses from APIs
        try:
            response = requests.get(url)
        except Exception:
            #maybe the Internet having some problems
            return None 
        if response.status_code == self.SUCCESS_RESPONSE_CODE:
            #nice, we're good to go, nothing went wrong
            return response.json()
        elif response.status_code == self.ERROR_RESPONSE_CODE:
            #handle error returned by the API
            self.api_error_handler(response.json())
            return None
        else:
            return None

    def get_comments(self, post_id, next_page = ''):
        #getting comments from a post
        api_url = self.API_GET_COMMENTS.format(post_id, self.comment_limit, next_page)
        comments = self.http_request(api_url)
        if comments:
            return comments
        else:
            print('Can\'t get comments from [{0}]...'.format(post_id))
            print(api_url)
            return {}

    def get_posts(self, page_id, next_page = ''):
        #getting posts from a fanpage
        api_url = self.API_GET_POSTS.format(page_id, self.post_limit, next_page)
        posts = self.http_request(api_url)
        if posts:
            return posts
        else:
            print('Can\'t get posts from [{0}]...'.format(page_id))
            print(api_url)
            return {}

    def dump_posts(self, page_id, next_page = ''):
        posts = self.get_posts(page_id, next_page)
        if not posts == {}:
            for post in posts['data']:
                self.write_email('[{0}]'.format(post['id']))
                #checking if the post is extracted before
                if not post['id'] in self.extracted_posts:
                    self.dump_comments(post['id'])
                else:
                    print('[{0}] extracted, skipping...'.format(post['id']))
            #check if there're more posts
            if 'paging' in posts and 'next' in posts['paging'] and self.get_all_posts == True:
                self.dump_posts(page_id, next_page = posts['paging']['next'])

    def dump_comments(self, post_id, next_page = ''):
        comment_count = 0
        email_count = 0
        comments = self.get_comments(post_id, next_page)
        if not comments == {}:
            for comment in comments['data']:
                comment_count += 1
                #extracting email addresses from comment
                emails = self.extract_email(comment['message'])
                if len(emails) == 0: 
                    #if this comment have no email, write down to check later
                    self.write_log(comment['message'])
                for email in emails:
                    commenter_name = comment['from']['name']
                    commenter_id = comment['from']['id']
                    if self.csv == True:
                        self.write_email('{0}, {1}, {2}'.format(email, commenter_name, commenter_id))
                    else:
                        self.write_email('{0} - {1} ({2})'.format(email, commenter_name, commenter_id))                        
                    email_count += 1
            #check if there're more comments
            if 'paging' in comments and 'next' in comments['paging'] and self.get_all_comments == True:
                self.dump_comments(post_id, next_page = comments['paging']['next'])
        print('Post [{0}]  {1} / {2}'.format(post_id, email_count, comment_count))

    def extract_email(self, data):
        #extracting emails from comment
        match = re.findall(r'[\w\.-]+@[\w\.-]+', data)
        return match

    def api_error_handler(self, http_response):
        #handle error returned by the API
        if http_response['error']:
            print(http_response['error']['message'])

    def write_log(self, log):
        with open(self.LOG_FILE_NAME, 'a', encoding='utf-8') as log_file:
            log_file.write('{0}\n'.format(log))

    def write_email(self, email):
        #write down extracted emails 
        if self.mode == 0:
            emails_file = 'exports/post/{0}.txt'.format(self.indentifier)
        elif self.mode == 1:
            emails_file = 'exports/page/{0}.txt'.format(self.indentifier)
        with open(emails_file, 'a', encoding='utf-8') as log_file:
            log_file.write('{0}\n'.format(email))

    def get_extracted_posts(self, indentifier):
        #get extracted posts list
        page_file_path = 'exports/{0}.txt'.format(self.indentifier)
        page_file = Path(page_file_path)
        if page_file.is_file():        
            match = re.findall(r'\[(.+)\]', page_file.read_text())
        return match        