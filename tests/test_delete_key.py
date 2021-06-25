import os
from unittest import mock

import pytest
from moto import mock_s3
from typer import Abort, Exit

from s3_tool.main import delete_key

from .test_login_data import bucket_contents


def test_delete_key_no_files(capsys):
    with pytest.raises(Abort):
        delete_key(files=[], prompt=False, threads=1)

        captured = capsys.readouterr()
        assert captured.out == "No files provided\n"


@mock.patch("s3_tool.main.get_login")
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
def test_delete_key_ending_with_delimiter(mock_bucket, capsys):
    with pytest.raises(Abort):
        mock_bucket.return_value = bucket_contents()
        delete_key(files=["source/"], prompt=False, threads=1)

        captured = capsys.readouterr()
        assert captured.out == "DO NOT DELETE A KEY ENDING WITH /\n"


@mock.patch(
    "s3_tool.main.get_login",
)
@mock_s3
def test_delete_key_starting_with_delimiter(mock_bucket, capsys):
    with pytest.raises(Abort):
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
        files=["source/empty.txt", "delimiter/delimiter/empty2.txt"],
        prompt=False,
        threads=1,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "Deleted Key: source/empty.txt\nDeleted Key: delimiter/delimiter/empty2.txt\n"
    )


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_delete_non_existing_key_no_prompt(mock_bucket, capsys):
    with pytest.raises(Abort):

        mock_bucket.return_value = bucket_contents()

        delete_key(
            files=["non_existing_file", "non_existing_file2"],
            prompt=False,
            threads=1,
        )

        captured = capsys.readouterr()
        print(captured.out)
        assert (
            captured.out
            == "non_existing_file does not exists!\nnon_existing_file2 does not exists!\n"
        )
