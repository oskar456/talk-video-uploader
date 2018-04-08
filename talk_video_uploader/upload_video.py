
import http.client
import httplib2
import random
import time
import json
import os
import sys

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

import click

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError,
                        http.client.NotConnected,
                        http.client.IncompleteRead,
                        http.client.ImproperConnectionState,
                        http.client.CannotSendRequest,
                        http.client.CannotSendHeader,
                        http.client.ResponseNotReady,
                        http.client.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow
# other types of access.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


def save_credentials(creds, filename):
    creds_data = {
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    try:
        os.makedirs(os.path.dirname(filename))
    except FileExistsError:
        pass
    with open(filename, "w") as outfile:
        json.dump(creds_data, outfile)


def get_authenticated_service(client_secrets, creds_file, local_server=False):
    """
    Either load or create authorization credentials
    and return service object.
    """
    try:
        credentials = Credentials.from_authorized_user_file(creds_file)
    except (ValueError, FileNotFoundError):
        credentials = None
    if not credentials:
        if not os.path.isfile(client_secrets):
            sys.exit("Missing client secrets file {}, "
                     "cannot proceed.".format(client_secrets))
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets,
                                                         SCOPES)
        if local_server:
            credentials = flow.run_local_server()
        else:
            credentials = flow.run_console()
        save_credentials(credentials, creds_file)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def do_upload(youtube, videofile, body):

    # Call the API's videos.insert method to create and upload the video.
    request = youtube.videos().insert(
        part=",".join(list(body.keys())),
        body=body,
        media_body=MediaFileUpload(videofile, chunksize=10*1024*1024,
                                   resumable=True)
    )

    response = None
    error = None
    retry = 0
    click.echo("Uploading file {}...".format(videofile))
    with click.progressbar(length=request.resumable.size()) as progress:
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress.update(status.resumable_progress)
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = "A retriable HTTP error {} occurred:\n{}".format(
                            e.resp.status, e.content)
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: {}".format(e)

            if error is not None:
                click.echo()
                click.echo(error)
                retry += 1
                if retry > MAX_RETRIES:
                    click.echo("No longer attempting to retry.", color="red")
                    return None

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                click.echo("Sleeping {} seconds and then retrying…".format(
                           sleep_seconds))
                time.sleep(sleep_seconds)
                error = None

    if "id" in response:
        click.echo("Video was successfully uploaded.")
        video_url = "https://www.youtube.com/watch?v={}".format(response["id"])
        return video_url
    else:
        click.echo("The upload failed with an unexpected "
                   "response: {}".format(response),
                   color="red")
        return None
