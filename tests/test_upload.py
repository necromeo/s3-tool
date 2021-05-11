import os
from pathlib import Path
from unittest import mock

import pytest
from moto import mock_s3
from typer import Abort

from s3_tool.main import create_upload_list, list_keys, upload

from .test_login_data import bucket_contents


def create_files(tmp_path, multiple=False):
    d = tmp_path / "upload-files"
    d.mkdir()

    if multiple:
        file_list = []
        for i in range(10):
            p = d / f"test_upload_file {i}.txt"
            p.write_text(f"Empty bodied file {i}")
            file_list.append(str(p))
        return file_list

    else:
        p = d / f"test_upload_file.txt"
        p.write_text("Empty bodied file")
        return str(p)


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_upload_one_file(mock_bucket, tmp_path, capsys):
    mock_bucket.return_value = bucket_contents()
    file_to_upload = create_files(tmp_path, multiple=False)

    upload(
        files=[file_to_upload],
        upload_path="test_upload_one_file",
        permissions="public-read",
        threads=1,
    )

    list_keys(
        prefix="test_upload_one_file",
        delimiter="",
        max_keys=1,
        key_methods="key",
        all=False,
        http_prefix=False,
        limit=1,
    )

    captured = capsys.readouterr()

    assert captured.out == "test_upload_one_file/test_upload_file.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_upload_multiple_files(mock_bucket, tmp_path, capsys):
    mock_bucket.return_value = bucket_contents()
    files_to_upload = create_files(tmp_path, multiple=True)

    upload(
        files=files_to_upload,
        upload_path="test_upload_multiple_files",
        permissions="public-read",
        threads=1,
    )

    list_keys(
        prefix="test_upload_multiple_files",
        delimiter="",
        max_keys=10,
        key_methods="key",
        all=False,
        http_prefix=False,
        limit=10,
    )

    captured = capsys.readouterr()

    expected_output = """test_upload_multiple_files/test_upload_file 0.txt
test_upload_multiple_files/test_upload_file 1.txt
test_upload_multiple_files/test_upload_file 2.txt
test_upload_multiple_files/test_upload_file 3.txt
test_upload_multiple_files/test_upload_file 4.txt
test_upload_multiple_files/test_upload_file 5.txt
test_upload_multiple_files/test_upload_file 6.txt
test_upload_multiple_files/test_upload_file 7.txt
test_upload_multiple_files/test_upload_file 8.txt
test_upload_multiple_files/test_upload_file 9.txt
"""

    assert captured.out == expected_output


def create_upload_list_for_testing(tmp_path):
    d = tmp_path / "upload-files"
    d.mkdir()
    for i in range(10):
        p = d / f"file {i}.txt"
        p.write_text(f"{i}")

    create_upload_list(
        files_path=d,
        file_extension="txt",
        output_path=d,
    )

    upload_txt_path = Path(os.path.join(d, "upload.txt"))

    return upload_txt_path


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_upload_from_file(mock_bucket, tmp_path, capsys):
    mock_bucket.return_value = bucket_contents()
    upload_file = create_upload_list_for_testing(tmp_path)

    upload(
        files=None,
        upload_from_file=upload_file,
        upload_path="test_upload_from_file",
        permissions="public-read",
        threads=3,
    )

    list_keys(
        prefix="test_upload_from_file",
        delimiter="",
        max_keys=10,
        key_methods="key",
        all=False,
        http_prefix=False,
        limit=10,
    )

    captured = capsys.readouterr()

    expected_output = """test_upload_from_file/file 0.txt
test_upload_from_file/file 1.txt
test_upload_from_file/file 2.txt
test_upload_from_file/file 3.txt
test_upload_from_file/file 4.txt
test_upload_from_file/file 5.txt
test_upload_from_file/file 6.txt
test_upload_from_file/file 7.txt
test_upload_from_file/file 8.txt
test_upload_from_file/file 9.txt
"""
    assert captured.out == expected_output


def test_upload_is_not_file(tmp_path):
    with pytest.raises(Abort):

        upload(
            files=["None"],
            upload_from_file=None,
            upload_path="test_upload_from_file",
            permissions="public-read",
            threads=3,
        )
