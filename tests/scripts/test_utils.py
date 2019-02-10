import json
import os
import tempfile

import click
import pytest

# noinspection PyProtectedMember
from infoblox.scripts.utils import (
    pretty_echo, _get_delimiter, _parse_item, parse_dict_items, handle_json_file, handle_json_arguments,
    check_environment, handle_dot_env_file
)


@pytest.fixture
def container(client):
    class Container:
        def __init__(self):
            self.client = client

    return Container()


@pytest.fixture
def command():
    return click.Command('foo')


@pytest.fixture
def context(client, command):
    class Container:
        def __init__(self):
            self.client = client

    click_context = click.Context(command)
    click_context.obj = Container()
    return click_context


def check_dict_items(data: dict, captured: str) -> None:
    for key, value in data.items():
        assert key in captured
        assert str(value) in captured


def test_pretty_echo(capsys):
    data = '2'
    pretty_echo(data)
    captured = capsys.readouterr().out
    assert data in captured

    data = {'foo': 2, 'hello': 'world'}
    pretty_echo(data)
    captured = capsys.readouterr().out
    check_dict_items(data, captured)

    data = [2, 'hello', {'foo': 'bar'}]
    pretty_echo(data)
    captured = capsys.readouterr().out
    for item in data:
        if isinstance(item, dict):
            check_dict_items(item, captured)
        else:
            assert str(item) in captured


class TestHandleJsonFile:
    # test option callback handle_json_file
    def test_function_prints_infoblox_result(self, capsys, responses, url, tempdir, context, command):
        def request_callback(request):
            return 200, {}, request.body

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        data = {'foo': 'bar'}
        test_file = os.path.join(tempdir, 'test.json')
        json.dump(data, open(test_file, 'w'))

        with pytest.raises(click.exceptions.Exit):
            # noinspection PyTypeChecker
            handle_json_file(context, command, test_file)
        captured = capsys.readouterr().out

        assert 'foo' in captured
        assert 'bar' in captured

    def test_function_prints_error_if_infoblox_returns_error_message(self, capsys, responses, url, tempdir, context,
                                                                     command):
        def request_callback(*_):
            return 400, {}, json.dumps({'error': 'oops'})

        responses.add_callback(responses.POST, f'{url}/request', callback=request_callback,
                               content_type='application/json')

        data = {'foo': 'bar'}
        test_file = os.path.join(tempdir, 'test.json')
        json.dump(data, open(test_file, 'w'))

        with pytest.raises(click.exceptions.Exit):
            # noinspection PyTypeChecker
            handle_json_file(context, command, test_file)

        captured = capsys.readouterr().out
        assert 'error' in captured
        assert 'oops' in captured

    def test_function_raises_error_if_file_can_not_be_dumped(self, tempdir, context, command):
        test_file = os.path.join(tempdir, 'test.csv')
        with open(test_file, 'w') as f:
            f.writelines(['header1,header2\n', 'foo,bar'])

        with pytest.raises(click.BadParameter) as exc_info:
            # noinspection PyTypeChecker
            handle_json_file(context, command, test_file)

        assert f'{test_file} is not a valid json file' == str(exc_info.value)

    def test_function_does_nothing_if_json_file_is_none(self, context, command):
        # noinspection PyTypeChecker
        assert handle_json_file(context, command, None) is None


class TestGetDelimiter:
    # test function _get_delimiter
    @pytest.mark.parametrize(('item', 'expected_delimiter'), [
        ('foo=bar', '='),
        ('foo:=2', ':=')
    ])
    def test_functions_returns_correct_delimiter(self, item, expected_delimiter):
        assert expected_delimiter == _get_delimiter(item)

    @pytest.mark.parametrize('item', ['foo', '{"foo": "bar"}'])
    def test_function_returns_none_when_there_is_no_delimiter(self, item):
        assert _get_delimiter(item) is None

    @pytest.mark.parametrize('item', ['=foo', 'foo=', ':=foo', 'foo:='])
    def test_function_raises_error_when_delimiter_starts_or_ends_an_item(self, item):
        with pytest.raises(click.UsageError) as exc_info:
            _get_delimiter(item)

        assert 'must not starts or ends an item like in' in str(exc_info.value)

    @pytest.mark.parametrize('item', ['foo=bar=stack', 'foo:=bar:=stack'])
    def test_function_raises_error_when_delimiter_presence_is_more_than_once(self, item):
        with pytest.raises(click.UsageError) as exc_info:
            _get_delimiter(item)

        assert f'{item} contains more than one occurrence of' in str(exc_info.value)


class TestParseItem:
    # test function _parse_item
    @pytest.mark.parametrize(('item', 'expected_dict'), [
        ('foo=bar', {'foo': 'bar'}),
        ('foo=2', {'foo': '2'}),
        ('foo:=2', {'foo': 2}),
        ('is_correct:=false', {'is_correct': False}),
        ('hobbies:=["http", "pies"]', {'hobbies': ['http', 'pies']}),
        ('article:={"foo": "bar"}', {'article': {'foo': 'bar'}})
    ])
    def test_function_correctly_parses_dict_items(self, item, expected_dict):
        assert expected_dict == _parse_item(item)

    @pytest.mark.parametrize('item', ['foo:=bar', 'foo:=False'])
    def test_function_raises_error_if_item_is_not_json_loadable(self, item):
        with pytest.raises(click.UsageError) as exc_info:
            _parse_item(item)

        assert f'unable to parse json data, this input is not correct: {item}' == str(exc_info.value)


class TestParseDictItems:
    # test function parse_dict_items
    @pytest.mark.parametrize(('item', 'expected_result'), [
        ('["http","pies"]', ['http', 'pies']),
        ('{"foo":"bar"}', {'foo': 'bar'}),
        ('foo=bar', {'foo': 'bar'})
    ])
    def test_function_returns_a_dict_when_a_single_tuple_element_is_passed(self, item, expected_result):
        assert expected_result == parse_dict_items((item,))

    @pytest.mark.parametrize('item', [
        'foo',
        "['foo']"  # in this case the string is created via str which is incompatible with json format
    ])
    def test_function_raises_error_when_single_element_provided_is_not_json_loadable(self, item):
        with pytest.raises(click.UsageError) as exc_info:
            parse_dict_items((item,))

        assert f'unable to parse json data, this input is not correct: {item}' == str(exc_info.value)

    @pytest.mark.parametrize(('items', 'expected_result'), [
        (('foo=bar', 'titi=2'), {'foo': 'bar', 'titi': '2'}),
        (('foo:=2', 'bar:=false'), {'foo': 2, 'bar': False}),
        (('hobbies:=["http", "pies"]', 'article:={"foo": "bar"}'),
         {'hobbies': ['http', 'pies'], 'article': {'foo': 'bar'}})
    ])
    def test_function_returns_correct_dict_when_multiple_items_are_provided(self, items, expected_result):
        assert expected_result == parse_dict_items(items)

    @pytest.mark.parametrize('items', [
        ('foo=2', 'bar:=False'),
        ('foo:=2', 'bar:=toto')
    ])
    def test_function_raises_error_when_some_items_are_not_json_loadable(self, items):
        with pytest.raises(click.UsageError) as exc_info:
            parse_dict_items(items)

        assert 'unable to parse json data' in str(exc_info.value)


class TestHandleJsonArguments:
    # test callback function handle_json_arguments

    def test_function_does_nothing_if_argument_is_none(self, context, command):
        # noinspection PyTypeChecker
        assert handle_json_arguments(context, command, None) is None

    @pytest.mark.parametrize(('items', 'expected_result'), [
        (('foo=bar',), {'foo': 'bar'}),
        (('foo=bar', 'shoes:=2'), {'foo': 'bar', 'shoes': 2})
    ])
    def test_function_prints_infoblox_result(self, context, command, items, expected_result):
        # noinspection PyTypeChecker
        assert expected_result == handle_json_arguments(context, command, items)


class TestCheckEnvironment:
    # test function check_environment
    @pytest.mark.parametrize(('environment', 'missing_env_var'), [
        ({'IB_USER': 'foo', 'IB_PASSWORD': 'bar'}, 'IB_URL'),
        ({'IB_USER': 'foo', 'IB_URL': 'bar'}, 'IB_PASSWORD'),
        ({'IB_PASSWORD': 'foo', 'IB_URL': 'bar'}, 'IB_USER'),
    ])
    def test_function_raises_error_if_env_variable_is_missing(self, monkeypatch, env_vars, environment,
                                                              missing_env_var):
        # conftest initializes these environment variables, so we need first to remove these
        # environment variables
        for key in env_vars:
            monkeypatch.delenv(key)
        for key, value in environment.items():
            monkeypatch.setenv(key, value)
        with pytest.raises(click.UsageError) as exc_info:
            check_environment()

        assert f'{missing_env_var} environment variable must be set before using ib.' == str(exc_info.value)

    def test_function_does_not_raises_error_when_env_variables_are_set(self):
        try:
            # conftest already initializes these environment variables
            check_environment()
        except click.UsageError:
            pytest.fail('check_environment fails with env variables set')


class TestHandleDotEnvFile:

    def test_function_loads_env_variables_when_dot_env_file_exists(self):
        with tempfile.TemporaryDirectory() as tempdir:
            env_path = os.path.join(tempdir, '.env')
            dad, mom = 'dad', 'mom'

            with open(env_path, 'w') as stream:
                stream.writelines([f'FATHER={dad}\n', f'MOTHER={mom}'])

            handle_dot_env_file(dot_env_file=env_path)

            assert os.getenv('FATHER') == dad
            assert os.getenv('MOTHER') == mom

    def test_function_raises_error_when_load_dotenv_raises_error(self, mocker):
        is_file_mock = mocker.patch('os.path.isfile')
        is_file_mock.return_value = True
        load_dotenv_mock = mocker.patch('dotenv.load_dotenv')
        load_dotenv_mock.side_effect = KeyError

        with pytest.raises(click.FileError):
            handle_dot_env_file()
