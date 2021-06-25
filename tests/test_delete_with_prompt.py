import os
from unittest import mock

import pytest
from moto import mock_s3
from typer import Abort, Exit

from s3_tool.main import delete_key

from .test_login_data import bucket_contents

"""
Must be run with -s or --capture=no flag!
Input is "y" first, "n" second.
"""


@pytest.mark.needs_input
@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_delete_key_one_file_prompt_positive(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()
    delete_key(files=["source/empty.txt"], prompt=True, threads=1)

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert (
        captured.out
        == "Are you sure you want to delete -> source/empty.txt? [y/N]: Deleted Key: source/empty.txt\n"
    )


@pytest.mark.needs_input
@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_delete_key_one_file_prompt_negative(mock_bucket, capsys):
    with pytest.raises(Exit):
        mock_bucket.return_value = bucket_contents()
        delete_key(files=["source/empty.txt"], prompt=True, threads=1)

        assert mock_bucket.called == True
        captured = capsys.readouterr()
        assert (
            captured.out
            == "Are you sure you want to delete -> source/empty.txt? [y/N]: Got cold feet?\n"
        )
