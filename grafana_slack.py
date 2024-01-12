import os
from flask import Flask, Response, request
import asyncio
from playwright.async_api import async_playwright
import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import urllib.parse
import logging

slack_token = os.environ["SLACK_BOT_TOKEN"]
slack = WebClient(token=slack_token)
logger = logging.getLogger()
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/url_v2", methods=["POST"])
async def post_url_v2():
    req = request.form
    req_dict = req.to_dict(flat=False)
    image_url = req_dict.get("text")[0]
    channel_id = req.get("channel_id")
    print(image_url)
    print(channel_id)

    async with async_playwright() as p:
        for browser_type in [p.chromium]:
            browser = await browser_type.launch()
            page = await browser.new_page()
            await page.goto(image_url)
            file_name = f"{datetime.date.today()}_image.png"
            await page.screenshot(path=file_name)
            await browser.close()
            try:
                result = slack.files_upload(
                    channels=channel_id,
                    initial_comment="image",
                    file=file_name,
                )
                logger.info(result)
            except SlackApiError as e:
                logger.error("Error uploading file: {}".format(e))

    return Response(status=200)



@app.route("/url", methods=["POST"])
async def post_url():
    req = request.json
    image_url = req.get("event").get("links")[0].get("url")
    channel_id = req.get("event").get("channel")

    async with async_playwright() as p:
        for browser_type in [p.chromium]:
            browser = await browser_type.launch()
            page = await browser.new_page()
            await page.goto(image_url)
            file_name = f"{datetime.date.today()}_image.png"
            await page.screenshot(path=file_name)
            await browser.close()
            try:
                result = slack.files_upload(
                    channels=channel_id,
                    initial_comment="image",
                    file=file_name,
                )
                logger.info(result)
            except SlackApiError as e:
                logger.error("Error uploading file: {}".format(e))

    return Response(status=200)
