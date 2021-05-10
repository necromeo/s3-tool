import os
from datetime import datetime
from unittest import mock

import pytest
from moto import mock_s3

from s3_tool.main import delete_key, _deleter

from .test_login_data import bucket_contents


def test_delete_key_no_files(capsys):
    delete_key(files=[], prompt=False, threads=1)

    captured = capsys.readouterr()
    assert captured.out == "No files provided\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_delete_key_one_file_no_prompt(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(files=["source/empty.txt"], prompt=False, threads=1)

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "Deleted Key: source/empty.txt\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_delete_key_one_file_prompt(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(files=["source/empty.txt"], prompt=True, threads=1)

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out == "Are you sure you want to delete -> source/empty.txt? [y/N]: "
    )


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_delete_key_ending_with_delimiter(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(files=["source/"], prompt=False, threads=1)

    captured = capsys.readouterr()
    assert captured.out == "DO NOT DELETE A KEY ENDING WITH /\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_delete_key_starting_with_delimiter(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(files=["/source"], prompt=False, threads=1)

    captured = capsys.readouterr()
    assert captured.out == "DO NOT DELETE A KEY STARTING WITH /\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_delete_multiple_keys_no_prompt(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(
        files=["source/empty.txt", "delimiter/delimiter/empty.txt"],
        prompt=False,
        threads=2,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "Deleted Key: source/empty.txt\nDeleted Key: delimiter/delimiter/empty.txt\n"
    )
