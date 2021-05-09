import os

import pytest

from s3_tool.main import bucket


@pytest.fixture
def env_variables():
    os.environ["ENDPOINT"] = "endpoint"
    os.environ["ACCESS_KEY"] = "access_key"
    os.environ["SECRET_ACCESS_KEY"] = "aws_secret_access_key"
    os.environ["HTTP_PREFIX"] = "https://http_prefix.com/"


# @pytest.fixture
def test_getting_enviroment_variables(env_variables):
    assert os.getenv("ENDPOINT") == "endpoint"
    assert os.getenv("ACCESS_KEY") == "access_key"
    assert os.getenv("SECRET_ACCESS_KEY") == "aws_secret_access_key"
    assert os.getenv("HTTP_PREFIX") == "https://http_prefix.com/"


def test_bucket():
    bucket_name = bucket("bucket_name")
    assert bucket_name == "bucket_name"

