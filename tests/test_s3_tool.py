import os
from unittest import mock

import boto3
import pytest
from moto import mock_s3
from typer.testing import CliRunner

from s3_tool import __version__
from s3_tool.main import app, bucket, get_login, list_keys

runner = CliRunner()


def test_version():
    assert __version__ == "0.3.1"


# contents is a bucket -> contents = s3.Bucket(name=bucket_name)


@pytest.fixture
def env_variables():
    os.environ["ENDPOINT"] = "endpoint"
    os.environ["ACCESS_KEY"] = "access_key"
    os.environ["SECRET_ACCESS_KEY"] = "aws_secret_access_key"
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"


@pytest.fixture()  # I'm doing something wrong here
def test_getting_enviroment_variables(env_variables):
    assert os.getenv("ENDPOINT") == "endpoint"
    assert os.getenv("ACCESS_KEY") == "access_key"
    assert os.getenv("SECRET_ACCESS_KEY") == "aws_secret_access_key"
    assert os.getenv("HTTP_PREFIX") == "https://http_prefix.com/"


def test_input_in_get_login():

    with mock.patch(
        "builtins.input",
        side_effect=[
            "https://s3.com",
            "aws_access_key_id",
            "aws_secret_access_key",
            "bucket",
        ],
    ):
        contents, s3, bucket_name, _ = get_login()
        assert contents == s3.Bucket(name="bucket")
        assert bucket_name == "bucket"


def test_bucket():
    bucket_name = bucket("bucket_name")
    assert bucket_name == "bucket_name"


@mock_s3
def bucket_contents():

    # Resource with bucket
    conn = boto3.resource(
        "s3",
    )
    bucket_name = "testing_bucket"
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    conn.create_bucket(Bucket=bucket_name)
    conn.Bucket(bucket_name).put_object(
        Key="source/empty", Body="Empty value", ACL="public-read"
    )
    contents = conn.Bucket(name=bucket_name)

    client = boto3.client("s3")

    return contents, conn, bucket_name, client


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_limit0_key(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="key",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit0_size(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="size",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty -> 0.0Mb\n"


# @mock.patch(
#     "s3_tool.main.get_login",
# )
# @mock_s3
# def test_list_keys_limit0_last_modified(mock_bucket, capsys):
#     """How could I fix the date?"""
#     mock_bucket.return_value = bucket_contents()

#     list_keys(
#         limit=0,
#         prefix="source/",
#         delimiter="",
#         max_keys=1,
#         all=False,
#         http_prefix=False,
#         key_methods="last_modified",
#     )

#     assert mock_bucket.called == True
#     captured = capsys.readouterr()
#     assert captured.out == "2021-05-06 16:29:57+00:00\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit0_owner(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="owner",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "{'DisplayName': 'webfile', 'ID': '75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a'}\n"
    )


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit0_acl(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods="acl",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "[{'Grantee': {'ID': '75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a', 'Type': 'CanonicalUser'}, 'Permission': 'FULL_CONTROL'}, {'Grantee': {'Type': 'Group', 'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'}, 'Permission': 'READ'}]\n"
    )


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit0_http_prefix(mock_bucket, capsys):
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"  # Can't add a @fixture >(
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=True,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "https://http_prefix.com/source/empty\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit0_all(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=True,
        http_prefix=False,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit0_all_http_prefix(mock_bucket, capsys):
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"  # Can't add a @fixture >(
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=True,
        http_prefix=True,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "https://http_prefix.com/source/empty\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit1_http_prefix(mock_bucket, capsys):
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"  # Can't add a @fixture >(
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=1,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=True,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "https://http_prefix.com/source/empty\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_list_keys_limit1(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=1,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=True,
        http_prefix=False,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty\n"
