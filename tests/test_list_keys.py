import os
from datetime import datetime
from unittest import mock

import pytest
from moto import mock_s3

from s3_tool.main import list_keys
from s3_tool.choices.object_methods import ObjectMethods

from .test_login_data import bucket_contents, env_variables


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_key(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys(
        limit=0,
        prefix="listkeys/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "listkeys/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_no_key(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys(
        limit=0,
        prefix="nothing_here/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == ""


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_size(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="listkeys/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=ObjectMethods.size,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "listkeys/empty.txt -> 0.0Mb\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_last_modified(mock_bucket, capsys):
    """How could I fix the date?"""
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="listkeys/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=ObjectMethods.last_modified,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_datetime = datetime.fromisoformat(captured.out.strip())
    assert type(captured_datetime) is datetime


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_owner(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="listkeys/",
        delimiter="",
        max_keys=1,
        all=False,
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
def test_list_keys_limit0_acl(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="listkeys/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=ObjectMethods.acl,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "[{'Grantee': {'ID': '75aa57f09aa0c8caeab4f8c24e99d10f8e7faeebf76c078efc7c6caea54ba06a', 'Type': 'CanonicalUser'}, 'Permission': 'FULL_CONTROL'}, {'Grantee': {'Type': 'Group', 'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'}, 'Permission': 'READ'}]\n"
    )


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_http_prefix(mock_bucket, capsys, env_variables):
    # os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"  # Can't add a @fixture >(
    prefix = f'{os.getenv("ENDPOINT")}'

    mock_bucket.return_value = bucket_contents()

    list_keys(
        limit=0,
        prefix="listkeys/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=True,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == f"{prefix}testing_bucket/listkeys/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_all(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys(
        limit=0,
        prefix="source/",  # This does NOTHING here!!
        delimiter="",
        max_keys=10,
        all=True,
        http_prefix=False,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()

    objects = captured.out.split("\n")

    assert objects[0] == "delimiter/delimiter/empty2.txt"
    assert objects[-2] == "source/subdir/empty4.txt"  # objects[-1] == ""


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit0_all_http_prefix(mock_bucket, capsys, env_variables):
    prefix = f'{os.getenv("ENDPOINT")}'
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
    objects = captured.out.split("\n")
    assert len(objects) == 8
    assert objects[0] == f"{prefix}testing_bucket/delimiter/delimiter/empty2.txt"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_list_keys_limit1_http_prefix(mock_bucket, capsys, env_variables):
    prefix = f'{os.getenv("ENDPOINT")}'
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
    assert captured.out == f"{prefix}testing_bucket/source/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
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
    assert captured.out == "source/empty.txt\n"
