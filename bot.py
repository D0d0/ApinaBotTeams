# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Set, Optional

import requests
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import Attachment
from bs4 import BeautifulSoup


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    def __init__(self):
        response = requests.get('https://apina.biz/tags', cookies={'i_need_it_now': 'fapfap'}, timeout=2).text
        soup = BeautifulSoup(response, features='html.parser')

        self.tags: Set[str] = set()
        for x in soup.find('div', id='tags').findAll('a'):
            self.tags.add(x.get('href').split('/tag/')[-1])

    def get_random(self, tag: Optional[str] = None):
        if tag:
            url = f'https://apina.biz/random/{tag}'
        else:
            url = f'https://apina.biz/random'

        img_href = None
        retries = 0
        while not img_href:
            response = requests.get(url, cookies={'i_need_it_now': 'fapfap'}, timeout=2).text
            soup = BeautifulSoup(response, features='html.parser')
            img_parent_elm = soup.find(id='big_image')
            if img_parent_elm and img_parent_elm.find('img'):
                img_href = img_parent_elm.find('img').get('src')
            retries += 1

            if retries > 5:
                return None

        return img_href

    async def on_message_activity(self, turn_context: TurnContext):
        apina_list = ['apina', 'apinu', 'apiny', 'apine', 'apinou', 'apinkou', 'apině', 'apinka', 'apín', 'apino']
        if any(s in turn_context.activity.text.lower() for s in apina_list):
            chosen_tag = None
            mess = turn_context.activity.text.lower()
            for tag in self.tags:
                if tag.replace('%20', ' ').lower() in mess:
                    chosen_tag = tag
                    break
            reply = self.get_random(chosen_tag)
            if reply:
                await turn_context.send_activity(
                    MessageFactory.content_url(reply, text=reply, content_type='image/' + reply.split('.')[-1])
                )
