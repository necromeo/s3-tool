from unittest import mock

import pytest
from moto import mock_s3

from s3_tool.choices import access_types, object_methods
from s3_tool.main import list_keys, list_keys_v2, move_object

from .test_login_data import bucket_contents


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_one_object(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["source/empty.txt"],
        destination_path="source2",
        rename=None,
        permission=access_types.ACLTypes.public_read,
        threads=1,
    )

    list_keys(
        limit=0,
        prefix="source2/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == "source2/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_one_object_empty_destination(mock_bucket):
    mock_bucket.return_value = bucket_contents()

    with pytest.raises(Exception):
        move_object(
            origin_files=["source/empty.txt"],
            destination_path="",
            rename=None,
            permission=access_types.ACLTypes.public_read,
            threads=1,
        )


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_one_object_in_root(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["empty.txt"],
        destination_path="source2",
        rename=None,
        permission=access_types.ACLTypes.public_read,
        threads=1,
    )

    list_keys(
        limit=0,
        prefix="source2/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == "source2/empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_fail_move_non_existing_object(mock_bucket):
    mock_bucket.return_value = bucket_contents()

    # Should hit a typer.Exit Exception
    with pytest.raises(Exception):
        move_object(
            origin_files=["sourcez/empty.txt"],
            destination_path="source2",
            rename=None,
            permission=access_types.ACLTypes.public_read,
            threads=1,
        )

        assert mock_bucket.called == True


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_two_objects(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["source/empty.txt", "delimiter/delimiter/empty2.txt"],
        destination_path="source2",
        rename=None,
        permission=access_types.ACLTypes.public_read,
        threads=2,
    )

    list_keys(
        limit=0,
        prefix="source2/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()

    assert captured.out == "source2/empty.txt\nsource2/empty2.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_fail_on_destination_path_with_delimiter(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    with pytest.raises(Exception):
        move_object(
            origin_files=["source/empty.txt"],
            destination_path="source2/",
            permission=access_types.ACLTypes.public_read,
            threads=1,
        )

        assert mock_bucket.called == True
        captured = capsys.readouterr()

        assert captured.out == "Destination path should not end with '/'\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_delete_origin_object(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["source/empty.txt"],
        destination_path="source2",
        rename=None,
        permission=access_types.ACLTypes.public_read,
        threads=1,
    )

    list_keys_v2(
        prefix="source/empty.txt",
        delimiter="",
        max_keys=1,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "No key was found!\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_and_rename_one_object(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["source/empty.txt"],
        destination_path="",  # destination_path should be overriden when renaming
        rename="new_empty.txt",
        threads=1,
        permission=access_types.ACLTypes.public_read,
    )

    list_keys(
        limit=1,
        prefix="source/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "source/empty2.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_and_rename_one_object_many_sublevels(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["delimiter/delimiter/empty2.txt"],
        destination_path="",  # destination_path should be overriden when renaming
        rename="new_empty.txt",
        threads=1,
        permission=access_types.ACLTypes.public_read,
    )

    list_keys(
        limit=0,
        prefix="delimiter/",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    assert captured.out == "delimiter/delimiter/new_empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_and_rename_object_in_root(mock_bucket, capsys):
    mock_bucket.return_value = bucket_contents()

    move_object(
        origin_files=["empty.txt"],
        destination_path="",  # destination_path should be overriden when renaming
        rename="new_empty.txt",
        threads=1,
        permission=access_types.ACLTypes.public_read,
    )

    list_keys(
        limit=0,
        prefix="new_",
        delimiter="",
        max_keys=1,
        all=False,
        http_prefix=False,
        key_methods=object_methods.ObjectMethods.key,
    )

    assert mock_bucket.called == True
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == "new_empty.txt\n"


@mock.patch("s3_tool.main.get_login")
@mock_s3
def test_move_and_rename_more_than_one_object(mock_bucket):
    mock_bucket.return_value = bucket_contents()

    with pytest.raises(Exception):
        move_object(
            origin_files=["source/empty.txt", "delimiter/delimiter/empty2.txt"],
            destination_path="source",
            rename="new_empty.txt",
            threads=1,
            permission=access_types.ACLTypes.public_read,
        )
