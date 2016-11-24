import os
import httplib
import json

import yaml

from flask import Flask, request, redirect
import twilio.twiml

API_KEY = "AJO8AO39"

app = Flask(__name__)

def latlon2wtw(blob):
    """
    """
    parts = blob.split("=")
    lat,lon = parts[1].split(",")
    # get three words with Lat Lon
    conn = httplib.HTTPSConnection("api.what3words.com")

    request_url = "/v2/reverse?coords=" + \
                 "{lat}%2C{lon}".format(lat=lat,lon=lon) + \
                 "&key={api_key}".format(api_key=API_KEY) + \
                 "&lang=en&format=json&display=full"

    conn.request("GET", request_url)
    res = conn.getresponse()
    data_str = res.read()
    j = json.loads(data_str)
    words = j.get("words")
    return words

def wtw_lookup(tw="encounter.inhaled.mime"):
    wtw = yaml.safe_load(open("./wtw.yaml"))
    return wtw.get(tw)

def guess_format(blob):
    if "https://maps.google.com/maps?q=" in blob:
        return latlon2wtw(blob)
    # TODO: more guesses here
    return wtw_lookup(blob)


@app.route("/sms", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
    print request
    print request.__dict__
    three_words = request.values.get("Body", None)
    resp = twilio.twiml.Response()
    resp.message(wtw_lookup(three_words))
    return str(resp)


@app.route("/", methods=['GET', 'POST'])
def hello_monkey_mms():
    """Respond to incoming calls with a simple text message."""
    print request
    print request.__dict__
    #three_words = request.values.get("Body", None)
    # TODO: sanity check body; error handling
    words = guess_format(request.values.get("Body"))
    resp = twilio.twiml.Response()
    data = wtw_lookup(words)
    with resp.message(data.get("sms")) as m:
        m.media(data.get("mms"))
    return str(resp)

if __name__ == "__main__":
     app.debug = True
     port = int(os.environ.get("PORT", 33507))
     app.run(host='0.0.0.0', port=port)
