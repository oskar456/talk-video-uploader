import sys
import os
import collections

import yaml
import click

from .upload_video import get_authenticated_service, do_upload
from .dumper import yaml_dump


@click.command()
@click.option(
    "--client-secrets",
    metavar="<client_secrets_json_file>",
    show_default=True,
    type=click.Path(dir_okay=False),
    default=os.path.join(sys.prefix, "share", "talk-video-uploader",
                         "client_id.json"),
    help="Path to OAuth2 client secret JSON file. "
    "Only needed when generating new credentials.")
@click.option(
    "--credentials",
    metavar="<oauth2_credentials_json_file>",
    show_default=True,
    type=click.Path(dir_okay=False),
    default=os.path.join(
        click.get_app_dir("talk-video-uploader"),
        "youtube_credentials.json"
    ),
    help="Path to OAuth2 credentials JSON file. "
         "Will be generated if necessary.")
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False),
    metavar="<metadata_yaml_file>…")
def main(client_secrets, credentials, files):
    """
    Upload Pyvo videos with proper metadata.

    Client secrets are bundled but can be also obtained from Google for free.
    Credentials file will be generated if non-existent.
    """
    youtube = get_authenticated_service(client_secrets, credentials)
    pyvometa = collections.defaultdict(list)
    for f in files:
        fbase, fext = os.path.splitext(f)
        if fext.lower() not in [".yaml", ".yml"]:
            click.echo(click.style("Ignoring file {} with unknown "
                       "extension.".format(f), fg="red"))
            continue
        try:
            with open(f) as inf:
                meta = yaml.safe_load(inf)
        except FileNotFoundError:
            click.echo(click.style("Metadata file {} not found!".format(f),
                                   fg="red"))
            continue
        videofile = meta.get("fname")
        if videofile:
            videofile = os.path.join(os.path.dirname(f), videofile)
        else:
            videofile = fbase + ".mkv"
        if not os.path.exists(videofile):
            click.echo(click.style("Video file {} "
                                   "not found!".format(videofile), fg="red"))
            continue

        tags = ["Python", "Pyvo"]
        if meta.get("lightning"):
            meta["lt"] = "\N{HIGH VOLTAGE SIGN} "
            tags.append("Lightning talk")
        else:
            meta["lt"] = ""

        youtube_body = {
            "snippet": {
                "title": "{lt}{speaker} – {title}".format_map(meta),
                "description": "{event} – {date}\n{url}".format_map(meta),
                "tags": tags,
                "categoryId": 27,  # Education
                },
            "status": {
                "privacyStatus": "unlisted",
                },
            "recordingDetails": {
                "recordingDate": "{date}T18:00:00.000Z".format_map(meta),
                },
        }

        lang = meta.get("language")
        if lang:
            if "audio" in lang:
                youtube_body["snippet"]["defaultAudioLanguage"] = lang["audio"]

        video_url = do_upload(youtube, videofile, youtube_body)
        if video_url:
            talkmeta = collections.OrderedDict()
            talkmeta["title"] = meta["title"]
            talkmeta["speakers"] = meta["speaker"].split(", ")
            if meta.get("lightning"):
                talkmeta["lightning"] = True
            if lang:
                talkmeta["language"] = lang
            talkmeta["coverage"] = [{"video": video_url}, ]
            talkyaml = yaml_dump([talkmeta, ])
            click.echo(talkyaml)
            pyvometa[meta["url"]].append(talkmeta)

    for url, talkmeta in pyvometa.items():
        click.echo(click.style(url, bold=True))
        click.echo("-"*len(url))
        click.echo(yaml_dump({"talks": talkmeta}))


if __name__ == "__main__":
    # pylint doesn't realize that click has changed the function signature.
    main()  # pylint: disable=no-value-for-parameter
