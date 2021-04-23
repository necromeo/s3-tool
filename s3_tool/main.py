import mimetypes
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import boto3
import botocore
import typer
from dotenv import load_dotenv
from tqdm import tqdm

from s3_tool.choices.access_types import ACLTypes
from s3_tool.choices.object_methods import ObjectMethods

load_dotenv()


app = typer.Typer(help="S3 CLI Tool to execute basic commands")


def bucket(bucket=os.getenv("BUCKET_NAME")) -> str:
    bucket_name = {"bucket": bucket}

    if bucket_name["bucket"] == None:
        bucket_name["bucket"] = input("Enter the name of your Bucket")

    return bucket_name["bucket"]


def get_login(
    endpoint=os.getenv("ENDPOINT"),
    access_key=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
):
    """Will prompt for your credentials if they are not in an .env file"""

    login_data = {
        "endpoint_url": endpoint,
        "aws_access_key_id": access_key,
        "aws_secret_access_key": aws_secret_access_key,
    }

    if login_data["endpoint_url"] == None:
        login_data["endpoint_url"] = input("Enter endpoint URL: ")
    if login_data["aws_access_key_id"] == None:
        login_data["aws_access_key_id"] = input("Enter your AWS Access Key: ")
    if login_data["aws_secret_access_key"] == None:
        login_data["aws_secret_access_key"] = input(
            "Enter your AWS Secret Access Key: "
        )

    s3 = boto3.resource(
        "s3",
        endpoint_url=login_data["endpoint_url"],
        aws_access_key_id=login_data["aws_access_key_id"],
        aws_secret_access_key=login_data["aws_secret_access_key"],
        use_ssl=True,
        config=botocore.config.Config(retries={"total_max_attempts": 3}),
    )

    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_ACCESS_KEY"),
    )

    login_data["bucket"] = bucket()

    # Bucket to be used
    bucket_name = login_data["bucket"]

    contents = s3.Bucket(name=bucket_name)

    return contents, s3, bucket_name, client


@app.command()
def list_keys(
    prefix: str = typer.Option(
        "source/", "--prefix", "-p", help="Prefix to look for keys"
    ),
    delimiter: str = typer.Option(
        "",
        "--delimiter",
        "-d",
        help="A delimiter is a character you use to group keys.",
    ),
    max_keys: int = typer.Option(
        1000,
        " --max-keys",
        "-mk",
        help="Sets the maximum number of keys returned in the response. The response might contain fewer keys but will never contain more.",
    ),
    http_prefix: bool = typer.Option(
        False, "--http-prefix", "-hp", help="Append HTTP URL Prefix to keys"
    ),
    all: bool = typer.Option(
        False, help="USE WITH CAUTION! If True, will fetch every key in the Bucket"
    ),
    limit: int = typer.Option(
        0, "--limit", "-l", help="Limits the amount of keys returned"
    ),
    key_methods: ObjectMethods = typer.Option(
        ObjectMethods.key, "--key-methods", "-km"
    ),
):
    """Lists keys according to a given prefix"""
    contents, _, _, _ = get_login()
    contar_http = os.getenv("HTTP_PREFIX") or ""

    if all is False and limit == 0:
        for obj in contents.objects.filter(
            Prefix=prefix, Delimiter=delimiter, MaxKeys=max_keys
        ):
            if http_prefix:
                typer.echo(f"{contar_http}{obj.key}")
            elif key_methods == "key":
                typer.echo(f"{obj.key}")
            elif key_methods == "size":
                typer.echo(f"{obj.key} -> {round(obj.size / 1024 ** 2, 2)}Mb")
            elif key_methods == "last_modified":
                typer.echo(f"{obj.last_modified}")
            elif key_methods == "owner":
                typer.echo(f"{obj.owner}")
            elif key_methods == "acl":
                typer.echo(obj.Acl().grants)
                # typer.echo(f"{obj.owner}")

    elif limit > 0:
        for obj in contents.objects.filter(
            Prefix=prefix, Delimiter=delimiter, MaxKeys=max_keys
        ).limit(count=limit):
            if http_prefix:
                typer.echo(f"{contar_http}{obj.key}")
            else:
                typer.echo(obj.key)
    else:
        for obj in contents.objects.all():
            if http_prefix:
                typer.echo(f"{contar_http}{obj.key}")
            else:
                typer.echo(obj.key)


@app.command()
def list_keys_v2(
    prefix: str = typer.Option(
        "source/", "--prefix", "-p", help="Prefix to look for keys"
    ),
    delimiter: str = typer.Option(
        "",
        "--delimiter",
        "-d",
        help="A delimiter is a character you use to group keys.",
    ),
    max_keys: int = typer.Option(
        1000,
        " --max-keys",
        "-mk",
        help="Sets the maximum number of keys returned in the response. The response might contain fewer keys but will never contain more.",
    ),
    http_prefix: bool = typer.Option(
        False, "--http-prefix", "-hp", help="Append HTTP URL Prefix to keys"
    ),
    key_methods: ObjectMethods = typer.Option(
        ObjectMethods.key, "--key-methods", "-km"
    ),
):
    """
    Lists keys using the S3 client rather than Resource (used for the
    list-keys command). Allows the usage of a delimiter to limit the output
    to "subfolders". Only operation not possible is the checking of ACL Grants.
    """
    _, _, bucket, client = get_login()
    contar_http = os.getenv("HTTP_PREFIX") or ""

    if delimiter != "":
        result = client.list_objects(
            Bucket=bucket, Prefix=prefix, Delimiter=delimiter, MaxKeys=max_keys
        )
        for o in result.get("CommonPrefixes"):
            typer.echo(o.get("Prefix"))

    elif http_prefix:
        result = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=max_keys)
        for x in result.get("Contents"):
            typer.echo(f'{contar_http}{x.get("Key")}')
    else:
        result = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=max_keys)

        for x in result.get("Contents"):
            if key_methods == "key":
                typer.echo(x.get("Key"))
            elif key_methods == "size":
                typer.echo(f"{x.get('Key')} -> {round(x.get('Size') / 1024 ** 2, 2)}Mb")
            elif key_methods == "last_modified":
                typer.echo(x.get("LastModified"))
            elif key_methods == "owner":
                typer.echo(x.get("Owner"))


def permission_changer(f, permissions):
    # Could check the permissions to know if to change them or not
    try:
        f.Acl().put(ACL=permissions.value)
    except Exception as e:
        typer.echo(f"Error -> {e}", err=True)


def file_gatherer(video_ids: str, changer_threads: int, permissions: str):
    contents, _, _, _ = get_login()
    all_files = [obj for obj in contents.objects.filter(Prefix=str(video_ids),)]

    progbar = tqdm(total=len(all_files), desc="files", unit="S3 files")
    with ThreadPoolExecutor(max_workers=changer_threads) as executor:
        results = [
            executor.submit(permission_changer, file, permissions) for file in all_files
        ]

        for res in results:
            progbar.update()
            res.result()
        progbar.close()


@app.command()
def change_permissions(
    args: List[str],
    prefix_threads: int = typer.Option(
        3, help="Sets the amount of prefixes that should be queried in parallel"
    ),
    changer_threads: int = typer.Option(
        50,
        help="Sets the amount of threads used to change permissions for a given prefix",
    ),
    permissions: ACLTypes = typer.Option(
        ACLTypes.public_read, "--permissions", "-p", help="Changes the keys permissions"
    ),
):
    """Takes any number of keys and changes their permissions to public-read"""
    try:
        if not args:
            typer.echo("You must specify at least one S3 Key")
        id_list = [str(i) for i in args]
        progbar = tqdm(total=len(id_list), desc="Total", unit="permission")

        with ThreadPoolExecutor(max_workers=prefix_threads) as executor:
            futures = [
                executor.submit(file_gatherer, vid_id, changer_threads, permissions)
                for vid_id in id_list
            ]
            for f in futures:
                progbar.update()
                f.result()
            progbar.close()
    except Exception as e:
        typer.echo(e)


def _deleter(k: str, prompt):
    _, s3, bucket_name, _ = get_login()

    if prompt:
        delete_prompt = typer.confirm(f"Are you sure you want to delete -> {k}?",)
        if not delete_prompt:
            typer.echo("Got cold feet?")
            raise typer.Abort()

    s3.Object(bucket_name, k).delete()
    message = "Deleted Key: "
    deleted = typer.style(f"{k}", fg=typer.colors.RED)
    typer.echo(message + deleted)


@app.command()
def delete_key(
    files: List[str] = typer.Option(
        None, "--files", "-f", help="Chose either a file or files with absolute path"
    ),
    prompt: bool = typer.Option(True, help="Display a prompt to confirm deletion"),
    threads: int = typer.Option(
        1,
        help="Set the amount of threads to delete keys in parallel. Disable the prompt if using this option",
    ),
):
    """USE WITH EXTREME CAUTION! Deletes a given key or keys"""
    try:
        if not files:
            typer.echo("No files provided")
            raise typer.Abort()

        for f in files:
            if f[0] == "/":
                typer.echo("DO NOT DELETE A KEY STARTING WITH /")
                raise typer.Abort()

        keys = [f for f in files]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(_deleter, k, prompt) for k in keys]
            for f in futures:
                f.result()

    except Exception as e:
        return e


def _upload_file(file_path: str, upload_path: str, upload_permission: str):
    contents, _, _, _ = get_login()

    file_name = Path(file_path).name
    key = f"{upload_path}/{file_name}"
    video_size = os.path.getsize(file_path)

    progbar = tqdm(
        total=video_size, unit="B", unit_scale=True, unit_divisor=1024, desc=file_name
    )

    def upload_progress(chunk):
        progbar.update(chunk)

    mimetype, _ = mimetypes.guess_type(file_path)

    if mimetype is None:
        mimetype = ""

    extra_args = {"ContentType": mimetype, "ACL": upload_permission}

    contents.upload_file(
        Filename=file_path, Key=key, Callback=upload_progress, ExtraArgs=extra_args,
    )

    progbar.close()


@app.command()
def upload(
    upload_path: str = typer.Argument(
        ..., help="Do not end this path with a slash '/'"
    ),
    files: List[str] = typer.Option(
        None, "--files", "-f", help="Chose either a file or files with absolute path"
    ),
    upload_from_file: str = typer.Option(
        None,
        "--upload-from-file",
        "-ff",
        help="Upload using text file containing paths to files separated by commas (,)",
    ),
    permissions: str = typer.Option(
        "public-read",
        "--permissions",
        "-perms",
        help="Sets the permission for the uploaded file. Options are: 'private' | 'public-read' | 'public-read-write' | 'authenticated-read' | 'aws-exec-read' | 'bucket-owner-read' | 'bucket-owner-full-control'",
    ),
    threads: int = typer.Option(
        3, "--threads", "-t", help="Amount of threads used to upload in parallel"
    ),
):
    """
    Uploads a single file or multiple files. Files need to have their absolute path.
    The last argument passed will be the upload path.
    Optionally, one can choose the amount of threads that should be used.
    """

    if files:
        for file in files:
            if Path(file).is_file() == False:
                typer.echo("Your input is not a file!")
                raise typer.Abort()

    elif upload_from_file:
        with open(upload_from_file, "r") as file_paths:
            paths = file_paths.read().strip()
            separated_paths = paths.split(",")
            files = [p.strip() for p in separated_paths]

        for file in files:
            if Path(file).is_file() == False:
                typer.echo(f"{file} is not a file!")
                raise typer.Abort()

    executor = ThreadPoolExecutor(max_workers=threads)
    futures = [
        executor.submit(_upload_file, vid, upload_path, permissions) for vid in files
    ]
    for f in futures:
        f.result()


def _downloader(file_key, download_path):
    try:
        contents, _, _, _ = get_login()

        if download_path is None:
            download_path = os.getcwd()

        file = contents.Object(file_key)

        # Checks if object exists, else -> throws Exception
        file.load()

        filename = os.path.basename(file_key)

        progbar = tqdm(
            total=file.content_length,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=filename,
        )

        def download_progress(chunk):
            progbar.update(chunk)

        contents.download_file(
            file.key,
            os.path.join(download_path, f"{filename}"),
            Callback=download_progress,
        )

        progbar.close()

    except Exception as e:
        pre_msg = typer.style("Error downloading -> ", fg=typer.colors.RED)
        failed_key = f"{file_key}"
        message = pre_msg + failed_key
        typer.echo(message)
        typer.secho(f"{e}", fg=typer.colors.RED, err=True)


@app.command()
def download(
    download_path: str = typer.Argument(
        ...,
        help="Sets download path. Will download in the folder where the command is executed if none is set",
    ),
    files: List[str] = typer.Option(
        None,
        "--files",
        "-f",
        help="Either a file or files, or a text file containing paths to files separated by commas (,)",
    ),
    threads: int = typer.Option(
        3, "--threads", "-t", help="Amount of threads used to download in parallel"
    ),
):
    """Downloads a key or series of keys"""

    if not files:
        typer.echo("You must choose at least one file to download")
        raise typer.Abort()

    executor = ThreadPoolExecutor(max_workers=threads)
    futures = [executor.submit(_downloader, vid, download_path) for vid in files]
    for f in futures:
        f.result()


@app.command(name="create-upload-list")
def create_upload_list(
    files_path: str = typer.Argument(...),
    file_extension: str = typer.Argument(...),
    output_path: str = typer.Option(
        os.getcwd(),
        help="Choose an output path. Else, the file will be written on the folder where the command is executed",
    ),
):
    """
    Writes a text file of all files in a folder with a given extension that
    can be used together with the upload command to upload multiple files
    at once
    """

    p = Path(files_path)

    files = [file for file in p.iterdir() if Path(file).suffix == f".{file_extension}"]

    with open(os.path.join(output_path, "upload.txt"), "a") as upload_list:
        if sys.platform.startswith("win32"):
            upload_list.write(",".join(f"{file}" for file in files))
        elif sys.platform.startswith("linux"):
            upload_list.write(",".join(f'"{file}"' for file in files))
        else:
            typer.echo("OS not compatible")
            typer.Abort()

    return


if __name__ == "__main__":
    app()
