import click
import pytest

from infoblox.scripts.options import (
    params_option, return_fields_option, return_fields_plus_option, proxy_search_option, object_ref_option,
    schedule_time_option, schedule_now_option, schedule_predecessor_option, schedule_warn_level_option,
    approval_comment_option, approval_query_mode_option, approval_ticket_number_option, arguments_option
)
from tests.helpers import assert_equals_output, assert_in_output


@click.command()
@params_option
def hello_param(params):
    click.echo(params)


@click.command()
@arguments_option
def hello_arguments(arguments):
    click.echo(arguments)


@click.command()
@return_fields_option
def hello_return_fields(return_fields):
    click.echo(return_fields)


@click.command()
@return_fields_plus_option
def hello_return_fields_plus(return_fields_plus):
    click.echo(return_fields_plus)


@click.command()
@proxy_search_option
def hello_proxy(proxy_search):
    click.echo(proxy_search)


@click.command()
@object_ref_option
def hello_object(object_ref):
    click.echo(object_ref)


@click.command()
@schedule_time_option
def hello_schedule_time(schedule_time):
    click.echo(schedule_time)


@click.command()
@schedule_now_option
def hello_schedule_now(schedule_now):
    click.echo(schedule_now)


@click.command()
@schedule_predecessor_option
def hello_predecessor(predecessor_task):
    click.echo(predecessor_task)


@click.command()
@schedule_warn_level_option
def hello_warn(warn_level):
    click.echo(warn_level)


@click.command()
@approval_comment_option
def hello_comment(approval_comment):
    click.echo(approval_comment)


@click.command()
@approval_query_mode_option
def hello_query_mode(query_mode):
    click.echo(query_mode)


@click.command()
@approval_ticket_number_option
def hello_ticket_number(ticket_number):
    click.echo(ticket_number)


class TestParamsOption:
    @pytest.mark.parametrize(('options', 'message'), [
        (['-p', '{"network": "10.2.0.0/16"}'], "{'network': '10.2.0.0/16'}\n"),
        (['--params', '{"network": "10.2.0.0/16"}'], "{'network': '10.2.0.0/16'}\n")
    ])
    def test_option_works_with_both_short_and_long_arguments(self, runner, options, message):
        result = runner.invoke(hello_param, options)

        assert_equals_output(0, message, result)

    def test_method_raises_error_when_option_is_not_valid_json(self, runner):
        result = runner.invoke(hello_param, ['-p', "{'foo':'bar'}"])

        assert_in_output(2, 'is not a valid json value', result)


class TestArgumentsOption:
    @pytest.mark.parametrize(('options', 'message'), [
        (['-a', '{"network": "10.2.0.0/16"}'], "{'network': '10.2.0.0/16'}\n"),
        (['--arguments', '{"network": "10.2.0.0/16"}'], "{'network': '10.2.0.0/16'}\n")
    ])
    def test_command_prints_correct_output(self, runner, options, message):
        result = runner.invoke(hello_arguments, options)

        assert_equals_output(0, message, result)

    def test_command_prompts_message_when_option_is_missing(self, runner):
        result = runner.invoke(hello_arguments, input='{"network": "10.2.0.0/16"}\n')

        assert_in_output(0, "{'network': '10.2.0.0/16'}\n", result)

    def test_method_raises_error_when_option_is_not_valid_json(self, runner):
        result = runner.invoke(hello_arguments, ['-a', "{'foo':'bar'}"])

        assert_in_output(2, 'is not a valid json value', result)


class TestReturnFieldsOption:
    # this class will tests options return_fields and return_fields_plus
    @pytest.mark.parametrize(('input_data', 'expected_output'), [
        ('network,comment', "['network', 'comment']\n"),
        ('', "['']\n")
    ])
    def test_hello_return_fields_option_prints_correct_data(self, runner, input_data, expected_output):
        result = runner.invoke(hello_return_fields, ['--return-fields', input_data])

        assert_equals_output(0, expected_output, result)

    @pytest.mark.parametrize(('input_data', 'expected_output'), [
        ('authority,ipv4addr', "['authority', 'ipv4addr']\n"),
        ('', "['']\n")
    ])
    def test_hello_return_fields_plus_option_prints_correct_data(self, runner, input_data, expected_output):
        result = runner.invoke(hello_return_fields_plus, ['--return-fields-plus', input_data])

        assert_equals_output(0, expected_output, result)


class TestProxySearchOption:
    @pytest.mark.parametrize('value', ['GM', 'LOCAL'])
    def test_command_prints_correct_output(self, runner, value):
        result = runner.invoke(hello_proxy, ['--proxy-search', value])

        assert_equals_output(0, f'{value}\n', result)

    def test_command_prints_local_when_option_is_not_specified(self, runner):
        result = runner.invoke(hello_proxy)

        assert_equals_output(0, 'LOCAL\n', result)

    @pytest.mark.parametrize('value', ['foo', 'Local'])
    def test_command_raises_error_when_option_value_is_not_correct(self, runner, value):
        result = runner.invoke(hello_proxy, ['--proxy-search', value])

        assert_in_output(2, f'invalid choice: {value}', result)


class TestObjectRefOption:
    @pytest.mark.parametrize(('option', 'input_data', 'expected_output'), [
        ('-o', 'a reference', 'a reference\n'),
        ('--object-ref', '1,2,3', '1,2,3\n')
    ])
    def test_command_prints_correct_output(self, runner, option, input_data, expected_output):
        result = runner.invoke(hello_object, [option, input_data])

        assert_equals_output(0, expected_output, result)

    def test_option_prompts_message_when_user_does_not_provide_it(self, runner):
        result = runner.invoke(hello_object, input='a reference\n')

        assert 0 == result.exit_code


class TestScheduleTimeOption:
    def test_command_prints_correct_output(self, runner):
        result = runner.invoke(hello_schedule_time, ['--schedule-time', '45'])

        assert_equals_output(0, '45\n', result)

    @pytest.mark.parametrize('value', ['foo', 'true'])
    def test_command_raises_error_if_option_is_not_valid_integer(self, runner, value):
        result = runner.invoke(hello_schedule_time, ['--schedule-time', value])

        assert_in_output(2, f'{value} is not a valid integer', result)


class TestScheduleNowOption:
    @pytest.mark.parametrize(('value', 'expected_output'), [
        ('true', 'True\n'),
        ('no', 'False\n'),
        ('yes', 'True\n')
    ])
    def test_command_prints_correct_output(self, runner, value, expected_output):
        result = runner.invoke(hello_schedule_now, ['--schedule-now', value])

        assert_equals_output(0, expected_output, result)

    def test_command_prints_false_when_no_option_is_provided(self, runner):
        result = runner.invoke(hello_schedule_now)

        assert_equals_output(0, 'False\n', result)


class TestSchedulePredecessorTaskOption:
    @pytest.mark.parametrize('value', ['foo', '1'])
    def test_command_prints_correct_output(self, runner, value):
        result = runner.invoke(hello_predecessor, ['--schedule-predecessor-task', value])

        assert_equals_output(0, f'{value}\n', result)


class TestScheduleWarnLevelOption:
    @pytest.mark.parametrize('value', ['WARN', 'NONE'])
    def test_command_prints_correct_output(self, runner, value):
        result = runner.invoke(hello_warn, ['--schedule-warn-level', value])

        assert_equals_output(0, f'{value}\n', result)

    def test_command_prints_none_if_no_option_is_provided(self, runner):
        result = runner.invoke(hello_warn)

        assert_equals_output(0, 'NONE\n', result)

    @pytest.mark.parametrize('value', ['none', 'Warn', 'foo'])
    def test_command_raises_error_if_option_is_invalid(self, runner, value):
        result = runner.invoke(hello_warn, ['--schedule-warn-level', value])

        assert_in_output(2, f'invalid choice: {value}', result)


class TestApprovalCommentOption:
    @pytest.mark.parametrize('value', ['foo', '1'])
    def test_command_prints_correct_output(self, runner, value):
        result = runner.invoke(hello_comment, ['--approval-comment', value])

        assert_equals_output(0, f'{value}\n', result)


class TestApprovalQueryModeOption:
    @pytest.mark.parametrize('value', ['true', 'false'])
    def test_command_prints_correct_output(self, runner, value):
        result = runner.invoke(hello_query_mode, ['--approval-query-mode', value])

        assert_equals_output(0, f'{value}\n', result)

    def test_command_prints_false_when_no_option_is_provided(self, runner):
        result = runner.invoke(hello_query_mode)

        assert_equals_output(0, 'false\n', result)

    @pytest.mark.parametrize('value', ['True', 'FALSE', '1'])
    def test_command_raises_error_when_option_is_invalid(self, runner, value):
        result = runner.invoke(hello_query_mode, ['--approval-query-mode', value])

        assert_in_output(2, f'invalid choice: {value}', result)


class TestApprovalTicketNumberOption:
    @pytest.mark.parametrize('value', ['4', '56'])
    def test_command_prints_correct_output(self, runner, value):
        result = runner.invoke(hello_ticket_number, ['--approval-ticket-number', value])

        assert_equals_output(0, f'{value}\n', result)

    @pytest.mark.parametrize('value', ['foo', '4.5'])
    def test_command_raises_error_when_option_is_invalid(self, runner, value):
        result = runner.invoke(hello_ticket_number, ['--approval-ticket-number', value])

        assert_in_output(2, f'{value} is not a valid integer', result)
