import json 
import requests
from pywebpush import webpush, WebPushException
import os
import scrapetube
import datetime
import time 
from requests import get
from bs4 import BeautifulSoup
import config
import builtins

def print(*args, **kwargs):
    # print to logs_file
    with open("logs_send.txt", "a+") as f:
        builtins.print(*args, file=f, **kwargs)
    # print to console
    return builtins.print(*args, **kwargs)


def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=config.private_key,
        vapid_claims=config.claims
    )

def send_discord_webhook(message):
    if  not config.discord_webhook:
        return
    
    data = {
        "content": message,
        "username": "Youtube Notifier"
    }
    requests.post(config.discord_webhook, json=data)

while True:
    if datetime.datetime.now().minute % 5 != 0:
        time.sleep(5)
        continue
    with open("data.json", "r") as f:
        data = json.load(f)

    try:
        data["subs"]
    except KeyError:
        data["subs"] = {}


    for channel in data["subs"]:
        print(channel)
        # check if the channel have new video/live stream
        # if yes then send notification to all subscribers
        
        # make a file videos.txt if not exist
        if not data["subs"][channel]:
            # should not care if there is no one to see the notification
            continue
        try:
            open("videos.txt", "r").close() 
        except FileNotFoundError:
            open("videos.txt", "w").close()
        with open("videos.txt", "r") as f:
            known_videos = f.read().split("\n")
        channel_link = f"https://youtube.com/channel/{channel}"
        html_data = get(channel_link).text
        soup = BeautifulSoup(html_data, 'html.parser')
        channel_name = soup.find("meta", property="og:title")["content"]
        channel_image = soup.find("meta", property="og:image")["content"]
        types = ['videos', 'shorts', 'streams']
        for type in types:
            print("doing type", type)
            videos = scrapetube.get_channel(channel, content_type=type, sort_by="newest")
            count = 0
            for video in videos:
                print(video["videoId"])
                count += 1
                if count > 1:
                    break
                with open("videos.json", "w") as f:
                    json.dump(video, f, indent=4)
                if type == "videos":
                    ago = video["publishedTimeText"]["simpleText"].lower()
                    if "day" in ago or "week" in ago or "month" in ago or "year" in ago:
                        break
                video_id = video["videoId"]
                if video_id not in known_videos:
                    # write video_id to videos.txt
                    with open("videos.txt", "a") as f:
                        f.write(video_id+"\n")
                    # send notification to all subscribers
                    for sub in data["subs"][channel]:
                        print(sub)
                        vtitle = video["headline"]["simpleText"] if type == "shorts" else video["title"]["runs"][0]["text"]
                        title = f"{channel_name} has posted a new video!" if type in ["videos", "shorts"] else f"{channel_name} is live now!"
                        _data = {
                                "title": title,
                                "body": vtitle,
                                "url": "https://youtube.com"+video["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"],
                                "icon": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                            }
                        _data = json.dumps(_data)
                        try:
                            send_web_push(sub, _data)
                        except WebPushException:
                            # remove that sub from data
                            data["subs"][channel].remove(sub)
                        except Exception as e:
                            print(e)

                        else:
                            print("sent")