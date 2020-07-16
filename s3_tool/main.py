import os, mimetypes
import typer
import boto3
from concurrent.futures import ThreadPoolExecutor
from typing import List
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

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
    )

    login_data["bucket"] = bucket()

    # Bucket to be used
    bucket_name = login_data["bucket"]

    contents = s3.Bucket(name=bucket_name)

    return contents, s3, bucket_name


@app.command()
def list_keys(
    prefix: str = typer.Option("source/", help="Prefix to look for keys"),
    http_prefix: bool = typer.Option(False, help="Append HTTP URL Prefix to keys"),
    all: bool = typer.Option(
        False, help="USE WITH CAUTION! If True, will fetch every key in the Bucket"
    ),
):
    """Lists keys according to a given prefix"""

    contents, _, _ = get_login()
    contar_http = os.getenv("HTTP_PREFIX") or ""

    if all is False:
        for obj in contents.objects.filter(Prefix=prefix):
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


def permission_changer(f, permissions: str):
    # Could check the permissions to know if to change them or not
    try:
        f.Acl().put(ACL=permissions)
    except Exception as e:
        typer.echo(f"Error -> {e}", err=True)


def file_gatherer(video_ids: str, changer_threads: int, permissions: str):
    contents, _, _ = get_login()
    all_files = [obj for obj in contents.objects.filter(Prefix=str(video_ids),)]

    with ThreadPoolExecutor(max_workers=changer_threads) as executor:
        results = [
            executor.submit(permission_changer, file, permissions) for file in all_files
        ]

        for res in results:
            res.result()


# TODO Add requested permission as parameter
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
    permissions: str = typer.Option(
        "public-read",
        help="Options are: 'private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control'",
    ),
):
    """Takes any number of keys and changes their permissions to public-read"""
    try:
        if not args:
            typer.echo("You must specify at least one S3 Key")
        id_list = [str(i) for i in args]
        progbar = tqdm(total=len(id_list), desc=permissions, unit="permission")

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
    _, s3, bucket_name = get_login()

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
    files: List[str],
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
        keys = [f for f in files]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(_deleter, k, prompt) for k in keys]
            for f in futures:
                f.result()

    except Exception as e:
        return e


def _upload_file(file_path: str, upload_path: str, upload_permission: str):
    contents, _, _ = get_login()

    file_name = Path(file_path).name
    key = f"{upload_path}/{file_name}"
    video_size = os.path.getsize(file_path)

    progbar = tqdm(
        total=video_size, unit="B", unit_scale=True, unit_divisor=1024, desc=file_name
    )

    def upload_progress(chunk):
        progbar.update(chunk)

    mimetype, _ = mimetypes.guess_type(file_path)

    extra_args = {"ContentType": mimetype, "ACL": upload_permission}

    contents.upload_file(
        Filename=file_path, Key=key, Callback=upload_progress, ExtraArgs=extra_args,
    )

    progbar.close()


@app.command()
def upload(
    files: List[str],
    upload_path: str,
    permissions: str = typer.Option(
        "public-read",
        help="Sets the permission for the uploaded file. Options are: 'private'|'public-read'|'public-read-write'|'authenticated-read'|'aws-exec-read'|'bucket-owner-read'|'bucket-owner-full-control'",
    ),
    worker_threads: int = typer.Option(
        3, help="Amount of threads used to upload in parallel"
    ),
):
    """
    Uploads a single file or multiple files. Files need to have their absolute path.
    The last argument passed will be the upload path.
    Optionally, one can choose the amount of threads that should be used.
    """

    executor = ThreadPoolExecutor(max_workers=worker_threads)
    futures = [
        executor.submit(_upload_file, vid, upload_path, permissions) for vid in files
    ]
    for f in futures:
        f.result()


def _downloader(file_key, download_path):
    try:
        contents, _, _ = get_login()

        if download_path is None:
            download_path = os.getcwd()

        file = contents.Object(file_key)

        # Checks if object exists, else -> throws Exception
        file.load()

        filename = os.path.basename(file_key)

        progbar = tqdm(
            total=file.size,
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
    files: List[str],
    download_path: str = typer.Option(
        None,
        help="Sets download path. Will download in the folder where the command is executed if none is set",
    ),
    worker_threads: int = typer.Option(
        3, help="Amount of threads used to download in parallel"
    ),
):
    """Downloads a key or series of keys"""

    executor = ThreadPoolExecutor(max_workers=worker_threads)
    futures = [executor.submit(_downloader, vid, download_path) for vid in files]
    for f in futures:
        f.result()


if __name__ == "__main__":
    app()
