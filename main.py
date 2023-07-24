import json, os

from flask import request, Response, render_template, jsonify, Flask, redirect
from pywebpush import webpush, WebPushException
from requests import get
from bs4 import BeautifulSoup
import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.secret_key



def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=config.private_key,
        vapid_claims=config.claims
    )

@app.before_request
def before_request():
    if not request.is_secure:
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)
    
@app.route('/')
def index():
    return "hello world"

@app.route("/c/<channel>/")
@app.route("/channel/<channel>/")
def channel(channel):
    data = {}
    channel_link = f"https://youtube.com/channel/{channel}"
    print("here")
    html_data = get(channel_link).text
    print("here")
    soup = BeautifulSoup(html_data, 'html.parser')
    channel_image = soup.find("meta", property="og:image")["content"]
    channel_name = soup.find("meta", property="og:title")["content"]
    data["channel_link"] = channel_link
    data["channelimage"] = channel_image
    # bgimage is channel banner
    data["bgimage"] = soup.find
    data["channelname"] = channel_name
    data["channel_id"] = channel
    return render_template("index.html", data=data)


@app.route("/subscription/", methods=["GET", "POST"])
def subscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """
    if request.method == "GET":
        return Response(response=json.dumps({"public_key": config.public_key}),
            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")
    
    subscription_token = request.get_json("subscription_token")
    print(subscription_token)
    if subscription_token["sub_token"] is None:
        return Response(status=201, mimetype="application/json")
    c = subscription_token['channel_id']
    del subscription_token['channel_id']
    subscription_token = json.loads(subscription_token["sub_token"])
    with open("data.json", "r") as f:
        data = json.load(f)
    try:
        data["subs"]
    except KeyError:
        data["subs"] = {}
    
    if c not in data["subs"]:
        data["subs"][c] = []

    if subscription_token in data["subs"][c]:    
        print("subscription token is already in data")
        return Response(status=201, mimetype="application/json")
    data["subs"][c].append(subscription_token)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
    _data = {}
    _data["title"] = "Welcome to the channel"
    _data["body"] = "You will be notified when the channel uploads a new video or goes live!"
    send_web_push(subscription_token, json.dumps(_data))
    return Response(status=201, mimetype="application/json")

@app.route("/unsubscription/", methods=["GET", "POST"])
def unsubscription():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """
    if request.method == "GET":
        return Response(response=json.dumps({"public_key": app.public_key}),
            headers={"Access-Control-Allow-Origin": "*"}, content_type="application/json")
    
    subscription_token = request.get_json("subscription_token")
    if subscription_token["sub_token"] is None:
        return Response(status=201, mimetype="application/json")
    c = subscription_token['channel_id']
    del subscription_token['channel_id']
    subscription_token = json.loads(subscription_token["sub_token"])
    with open("data.json", "r") as f:
        data = json.load(f)
    try:
        data["subs"]
    except KeyError:
        data["subs"] = {}
    
    if c not in data["subs"]:
        data["subs"][c] = []

    if subscription_token not in data["subs"][c]:    
        print("subscription token is not in data")
        return Response(status=201, mimetype="application/json")
    data["subs"][c].remove(subscription_token)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
    return Response(status=201, mimetype="application/json")

if __name__ == "__main__":
    app.run(ssl_context=('certificate.crt', 'private.key'), host='0.0.0.0', port=9999)

