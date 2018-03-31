import sys
import os

import yaml
import click

from .upload_video import get_authenticated_service, do_upload


@click.command()
@click.option(
    '--client-secrets',
    metavar='<client_secrets_json_file>',
    show_default=True,
    type=click.Path(exists=True, dir_okay=False),
    default=os.path.join(sys.prefix, 'share', 'talk-video-uploader',
                         'client_id.json'),
    help='Path to OAuth2 client secret JSON file.')
@click.option(
    '--credentials',
    metavar='<oauth2_credentials_json_file>',
    show_default=True,
    type=click.Path(exists=False, dir_okay=False),
    default=os.path.join(
        click.get_app_dir("talk-video-uploader"),
        "youtube_credentials.json"
    ),
    help='Path to OAuth2 credentials JSON file. Will be generated if necessary.')
@click.argument(
    'files',
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False),
    metavar='<metadata_yaml_file>…')
def main(client_secrets, credentials, files):
    """
    Upload Pyvo videos with proper metadata.

    Client secrets are bundled but can be also obtained from Google for free.
    Credentials file will be generated if non-existent.
    """
    youtube = get_authenticated_service(client_secrets, credentials)
    for f in files:
        fbase, fext = os.path.splitext(f)
        if fext.lower() not in ['.yaml', '.yml']:
            click.echo("Ignoring file {} with unknown "
                       "extension.".format(f), fg='red')
            continue
        try:
            with open(f) as inf:
                meta = yaml.safe_load(inf)
        except FileNotFoundError:
            click.echo("Metadata file {} not found!".format(f), fg='red')
            continue
        videofile = meta.get("fname")
        if videofile:
            videofile = os.path.join(os.path.dirname(f), videofile)
        else:
            videofile = fbase + ".mkv"
        if not os.path.exists(videofile):
            click.echo("Video file {} not found!".format(videofile), fg='red')
            continue

        tags = ["Python", "Pyvo"]
        if meta.get("lightning"):
            meta['lt'] = "\N{HIGH VOLTAGE SIGN} "
            tags.append("Lightning talk")
        else:
            meta['lt'] = ""
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

        video_url = do_upload(youtube, videofile, youtube_body)
        talkmeta = [{"title": meta['title'],
                     "speakers": meta['speaker'].split(", "),
                     "lightning": meta['lightning'],
                     "coverage": {"video": video_url},
                     }]
        talkyaml = yaml.safe_dump(talkmeta, default_flow_style=False,
                                  allow_unicode=True)
        click.echo(talkyaml)


if __name__ == '__main__':
    # pylint doesn't realize that click has changed the function signature.
    main()  # pylint: disable=no-value-for-parameter
