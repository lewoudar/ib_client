import pytest
import click

from infoblox.scripts.types import STRING_LIST, DICT


@pytest.mark.parametrize(('input_data', 'expected_output'), [
    ('foo,bar,1', "['foo', 'bar', '1']\n"),
    ('', "['']\n")
])
def test_param_type_returns_string_list_giving_comma_separated_list_as_input(runner, input_data, expected_output):
    @click.command()
    @click.option('-n', '--names', type=STRING_LIST)
    def hello(names):
        click.echo(names)

    result = runner.invoke(hello, ['-n', input_data])

    assert expected_output == result.output


class TestDictParamType:

    @pytest.mark.parametrize(('input_data', 'expected_output'), [
        ('{"foo":"bar"}', "{'foo': 'bar'}\n"),
        ('{"bag":1,"meters":2.5}', "{'bag': 1, 'meters': 2.5}\n"),
        ('"foo"', 'foo\n'),
        ('["a","b"]', "['a', 'b']\n")
    ])
    def test_param_type_returns_dict_giving_json_string_as_input(self, runner, input_data, expected_output):
        @click.command()
        @click.option('-j', '--json', 'json_string', type=DICT)
        def hello(json_string):
            click.echo(json_string)

        result = runner.invoke(hello, ['-j', input_data])

        assert expected_output == result.output

    def test_param_type_raises_error_if_input_data_is_not_valid_json(self, runner):
        @click.command()
        @click.option('-j', '--json', 'json_string', type=DICT)
        def hello(json_string):
            click.echo(json_string)

        input_data = 'foo'
        result = runner.invoke(hello, ['-j', input_data])

        assert 2 == result.exit_code
        assert f'{input_data} is not a valid json value' in result.output
