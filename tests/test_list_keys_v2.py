import os
from datetime import datetime
from unittest import mock

import pytest
from moto import mock_s3

from s3_tool.main import list_keys_v2

from .test_login_data import bucket_contents


@pytest.fixture
def env_variables():
    os.environ["ENDPOINT"] = "endpoint"
    os.environ["ACCESS_KEY"] = "access_key"
    os.environ["SECRET_ACCESS_KEY"] = "aws_secret_access_key"
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_v2_key(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods="key",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty.txt\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_v2_size(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods="size",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty.txt -> 0.0Mb\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_v2_last_modified(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods="last_modified",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    captured_datetime = datetime.fromisoformat(captured.out.strip())
    assert type(captured_datetime) is datetime


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_v2_http_prefix(mock_bucket, capsys, env_variables):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
        http_prefix=True,
        key_methods="key",
    )
    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "https://http_prefix.com/source/empty.txt\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_v2_owner(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="source/",
        delimiter="",
        max_keys=1,
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
@mock_s3  # This MUST be explicitly called when mocking the s3 call!!!
def test_list_keys_v2_delimiter(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    list_keys_v2(
        prefix="delimiter/",
        delimiter="/",
        max_keys=1,
        http_prefix=False,
        key_methods="key",
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "delimiter/delimiter/\n"
