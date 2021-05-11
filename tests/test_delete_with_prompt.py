import os
import pytest
from unittest import mock
from typer import Exit, Abort
from moto import mock_s3

from s3_tool.main import delete_key

from .test_login_data import bucket_contents

"""
Must be run with -s or --capture=no flag!
Input is "y" first, "n" second.
"""

# TODO Add markers here
# https://docs.pytest.org/en/6.2.x/example/markers.html
@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_delete_key_one_file_prompt_positive(mock_bucket, monkeypatch, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(files=["source/empty.txt"], prompt=True, threads=1)

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "Are you sure you want to delete -> source/empty.txt? [y/N]: Deleted Key: source/empty.txt\n"
    )


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_delete_key_one_file_prompt_negative(mock_bucket, monkeypatch, capsys):
    with pytest.raises(Exit):
        mock_bucket.return_value = bucket_contents()
        delete_key(files=["source/empty.txt"], prompt=True, threads=1)

        assert mock_bucket.called == True
