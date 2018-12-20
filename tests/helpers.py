"""Helper functions for tests"""
from click.testing import Result


# for click commands
def assert_list_items(exit_code: int, data: list, result: Result) -> None:
    assert exit_code == result.exit_code
    for item in data:
        assert item in result.output


def assert_in_output(exit_code: int, expected_output: str, result: Result) -> None:
    assert exit_code == result.exit_code
    assert expected_output in result.output


def assert_equals_output(exit_code: int, expected_output: str, result: Result) -> None:
    assert exit_code == result.exit_code
    assert expected_output == result.output
