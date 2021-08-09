import os
from datetime import datetime
from unittest import mock

import pytest
from moto import mock_s3

from s3_tool.main import list_keys_v2
from s3_tool.choices.object_methods import ObjectMethods

from .test_login_data import bucket_contents, env_variables


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_key(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods=ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_no_key(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="nothing_here/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods=ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "No key was found!\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_size(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods=ObjectMethods.size,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty.txt -> 0.0Mb\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_last_modified(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods=ObjectMethods.last_modified,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_datetime = datetime.fromisoformat(captured.out.strip())
    assert type(captured_datetime) is datetime


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_http_prefix(mock_bucket, capsys, env_variables):
    prefix = os.getenv("ENDPOINT")
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=True,
        key_methods=ObjectMethods.key,
    )
    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == f"{prefix}testing_bucket/source/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_owner(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods=ObjectMethods.owner,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "{'DisplayName': 'webfile', 'ID': '75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a'}\n"
    )


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_v2_delimiter(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="delimiter/",
        delimiter="/",
        max_keys=1,
        http_prefix=False,
        key_methods=ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "delimiter/delimiter/\n"
