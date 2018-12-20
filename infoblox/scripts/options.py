"""Common options used in different commands"""
import click

from .types import STRING_LIST, DICT

object_ref_option = click.option('-o', '--object-ref', help='reference of the object to fetch',
                                 prompt='object reference')

params_option = click.option('-p', '--params', help='query parameters used to filter results', type=DICT)

arguments_option = click.option('-a', '--arguments', prompt='arguments', type=DICT,
                                help='arguments to pass to the function / command in json format')

return_fields_option = click.option('--return-fields', help='comma-separated list of returned fields',
                                    type=STRING_LIST)

return_fields_plus_option = click.option('--return-fields-plus', type=STRING_LIST,
                                         help='comma-separated list of fields returned in addition of the basic fields'
                                              ' of the object')

proxy_search_option = click.option('--proxy-search', type=click.Choice(['GM', 'LOCAL']), default='LOCAL',
                                   help='processes requests on grid master or locally')

schedule_time_option = click.option('--schedule-time', type=int,
                                    help='a timestamp representing the time to execute the operation')

schedule_now_option = click.option('--schedule-now', type=bool, default=False,
                                   help="if set to true, the operation will be executed at the current time."
                                        " NB: you should set this option if you don't use option --schedule-time")

schedule_predecessor_option = click.option('--schedule-predecessor-task', 'predecessor_task',
                                           help='reference to a scheduled task that will be executed before'
                                                ' the submitted task')

schedule_warn_level_option = click.option('--schedule-warn-level', 'warn_level', type=click.Choice(['WARN', 'NONE']),
                                          default='NONE', help='warning level for the operation')

approval_comment_option = click.option('--approval-comment', help='comment for the approval operation')

approval_query_mode_option = click.option('--approval-query-mode', 'query_mode', type=click.Choice(['true', 'false']),
                                          default='false', help='query mode for the approval operation')

approval_ticket_number_option = click.option('--approval-ticket-number', 'ticket_number', type=int,
                                             help='ticket number for the approval operation')
