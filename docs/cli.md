# CLI

[TOC]

Before using the CLI, you will have to set 3 environment variables, otherwise you will have an error. The 3 environment
variables are:

- **IB_USER:** the user to connect to.
- **IB_PASSWORD:** the user's password.
- **IB_URL:** the wapi url which must be of the form `https://foo.com/wapi/v2.X`.

To not repeat yourself every time you need to use the CLI, you can create a `.env` file with the above environment
variables and put it in your working directory. `ib` command will automatically load this file so you can focus on
performing tasks.

To have an overview of what is possible to do with the CLI, it is important to know that there is an 
help (`-h`, `--help`) option available.

````console
ib -h
Usage: ib [OPTIONS] COMMAND [ARGS]...

  Infoblox Command Line Interface. It allows you to interact with infoblox
  in the same way you will do with the python api client.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  object            Performs various object operations.
  objects           Lists the available objects supports by the infoblox...
  request           Makes a custom request using the request object of...
  schema            Shows the api schema.
  shell-completion  Installs shell completion.
````

We will explain how to use the different commands but remember that the **help option** (`-h`) is available on every command
to help you understand it. Before digging into commands, we will first see all environment variables you can use
to customize the behaviour of the CLI.

## Environment variables

In addition to the three mentioned above, you also have:

- **DEFAULT_CONNECT_TIMEOUT**: a float value representing the time in seconds `ib` will wait to establish a connection
to the infoblox server. By default the connection timeout is **1.0** second.
- **DEFAULT_READ_TIMEOUT**: a float value representing the time in seconds `ib` will wait before receiving the first
byte from the infoblox server. The default value is **3.1** seconds.
- **DEFAULT_MAX_RETRIES**: an integer value representing the number of times `ib` will try to connect to the infoblox
server. The default value is **3**.
- **DEFAULT_BACKOFF_FACTOR**: this value is related to the previous one, it is a backoff factor to apply between
attempts after the second try. The default value is **0.2**. To understand how it works, know that if you have a
connection timeout of 1 s, 3 retries and a backoff factor of 0.2, the first retry will take `1 + 0.0 s`, the second,
`1 + 0.2 s` and the last `1 + 0.4 s`.

## Commands

## `shell-completion`

This command **should be** the first command you run in order to have completion for *options* and *commands*. Like it
is said in the help message, it only works on **bash**, **fish**, **zsh** and **PowerShell**.

#### arguments

- `SHELL`: the shell to use for completion. It will be guessed if not provided. The values available are listed in the
help message: `[bash|fish|zsh|powershell]`. Example usage: `ib shell-completion bash`.
- `PATH`: the installation path of the code to be evaluated by the shell. The standard installation path is used if
the argument is not provided. Example usage: `ib shell-completion /path/to/completion/file`.

#### options

- `--append / --overwrite`: whether or not to append the generated completion code to the completion file. The
default behaviour is to overwrite. Example usage: `ib shell-completion --append`.
- `-i`: this option if provided allows you to complete options and commands in a case insensitive manner.

## `objects`

This command lists all the available objects supported by the infoblox api. There are no options or arguments.

## `schema`

This command shows the infoblox api schema. It gives you a little more information than the `objects` command.

## `request`

This command allows you to perform custom requests like infoblox 
[allows](https://ipam.illinois.edu/wapidoc/additional/samplebodyrequests.html) it.

#### arguments

`JSON_DATA`: This argument if provided can be:

- a *JSON* string representing the body of the request. Example usage:
`ib request '{"data":{"name":"test.somewhere.com"},"method":"GET","object":"record:host"}'`.

!!! warning
    On windows, the string is represented with double quotes so, you will have to escape all strings within the JSON.
    Example: `ib request "{\"data\":{\"name\":\"test.somewhere.com\"},\"method\":\"GET\",\"object\":\"record:host\"}"`
    
- a series of `key=value` if you deals with a single json and not an array of json. To use the example above, 
we can do this: `ib request data:='{"name":"test.somewhere.com"}' method=GET object:='"record:host"'`. Note that `=`
separator is used for simple string values and `:=` separator is used for other JSON values (dict, arrays, numbers) or
ambiguous strings like `record:host`.

#### options

- `-j`: this option represents a path to a json file that **must** contains the body of the request. It is more flexible
than writing all of the JSON by hand in the shell, especially when the body is large. Example usage:
`ib request -j /path/to/json/file`

## `object`

This is the main command of the CLI. It wraps many sub commands that allows you to interact with infoblox api.

````console
Usage: ib object [OPTIONS] COMMAND [ARGS]...

  Performs various object operations.

Options:
  -n, --name TEXT  Wapi object you want to interact with.
  -h, --help       Show this message and exit.

Commands:
  count          Counts infoblox objects.
  create         Creates an infoblox object.
  delete         Deletes an infoblox object given its reference.
  documentation  Shows the documentation of the object's api.
  field-info     Shows the documentation of the object field.
  fields         Lists all object fields.
  func-call      Calls a function of an infoblox object.
  func-info      Shows the documentation of the object function.
  functions      Lists all object functions.
  get            Retrieves and shows objects matching given criteria.
  update         Updates an infoblox object given its reference.
````

#### options

- `-n, --name`: the name of the infoblox object with which we want to interact. It is one of the names returned by the
[objects](#objects) command.

#### sub commands

### `documentation`

This command shows the documentation of the object's api. Example usage: `ib object -n network documentation`.

### `fields`

This command lists fields of a specific object. For example to know all the fields available on the network object, we
can run this: `ib object -n network fields`.

### `functions`

This command lists functions of a specific object. For example to know all the functions available on the network object,
we can run this: `ib object -n network functions`.

### `field-info`

This command gives information about a specific object field like the type, how to search it, what operations can be
realized, etc...

Options:

- `-n, --name`: The name of the field whose information is wanted. Example usage:
`ib object -n network field-info -n comment`

### `func-info`

This command gives information about a specific object function like input fields, their type, what output fields are
expected, etc...

Options:

- `-n, --name`: The name of the function whose information is wanted. Example usage:
`ib object -n network func-info -n next_available_ip`

### `get`

This command retrieves objects corresponding to given criteria.

Options:

- `-o, --object-ref`: optional reference of the object to fetch. Example usage: `ib object -n network -o my-reference`.
- `-p, --params`: a json string representing parameters to filter results. Example usage:
`ib object -n network get -p '{"comment~":"just"}'`
- `--return-fields`: comma-separated list of fields to be returned. Example usage:
`ib object ... --return-fields=network,comment,networkview`
- `--return-fields-plus`: comma-separated list of fields to be returned in addition of the basic fields of the object.
Example usage: `ib object ... --return-fields-plus=utilization,ddns_ttl`.
- `--proxy-search`: specifies where to process requests. Two values are possible: `GM` for *grid master* and `LOCAL` for
locally.

### `count`

This command counts and shows the number of objects matching given parameters.

Options:

- `-p, --params`: a json string representing parameters to filter results. Example usage:
`ib object -n network count -p '{"comment~":"just"}'`
- `--proxy-search`: specifies where to process requests. Two values are possible: `GM` for *grid master* and `LOCAL` for
locally.

### `func-call`

This command calls a function of an infoblox object.

Options:

- `-n, --name`: name of the function call. Example usage: `ib object -n network func-call -n next_available_ip ...`
- `-o, --object-ref`: optional reference of the object to which the function is to be applied. Example usage:
`ib object -n network func-call -n next_available_ip -o my-reference ...`
- `-a, --arguments`: arguments to pass to the function in json format. Example usage:
`ib object -n network func-call -n next_available_ip -o my-reference -a '{"num":2}'`

### `create`

This command creates an infoblox object.

Options:

- `--schedule-time`: optional timestamp representing the date to perform the operation. Example usage:
`ib object -n network create --schedule-time=1599688800 ...`

- `--schedule-now`: optional boolean to execute the operation at the current time. You should set this option **only if
you don't use** option `--schedule-time`. Example usage: `ib object -n network create --schedule-now=yes ...`

- `--schedule-predecessor-task`: optional reference to a scheduled task that will be executed before the submitted task.
Example usage: `ib object -n network create --schedule-predecessor-task=task-reference ...`

- `--schedule-warn-level`: optional warn level for the operation. Possible values are `WARN` and `NONE`.
Example usage: `ib object -n network create --schedule-warn-level=WARN ...`

- `--approval-comment`: optional comment for the approval operation. Example usage:
`ib object -n network create --approval-comment='a comment' ...`

- `--approval-query-mode`: optional query mode for the approval operation. Possible values are `true` and `false`.
Example usage: `ib object -n network create --approval-query-mode=true ...`

- `--approval-ticket-number`: optional ticket number for the approval operation. Example usage:
`ib object -n network create --approval-ticket-number=11898 ...`

- `--return-fields`: comma-separated list of fields to be returned to check the created object.
Example usage: `ib object -n network create --return-fields=comment,utilization ...`

- `--return-fields-plus`: comma-separated list of fields to be returned in addition of the basic fields to check the
created object. Example usage: `ib object -n network create --return-fields-plus=netmask,utilization ...`

- `-a, --arguments`: a json string representing arguments to pass to the create command. Example usage:
`ib object -n network create -a '{"network":"10.1.0.0/16"}'`

### `update`

This command updates an infoblox object given its reference.

Options:

- `-o, --object-ref`: reference of the infoblox object to update. Example usage:
`ib object -n network update -o object-reference ...`

- `--schedule-time`: optional timestamp representing the date to perform the operation. Example usage:
`ib object -n network update --schedule-time=1599688800 ...`

- `--schedule-now`: optional boolean to execute the operation at the current time. You should set this option **only if
you don't use** option `--schedule-time`. Example usage: `ib object -n network update --schedule-now=yes ...`

- `--schedule-predecessor-task`: optional reference to a scheduled task that will be executed before the submitted task.
Example usage: `ib object -n network update --schedule-predecessor-task=task-reference ...`

- `--schedule-warn-level`: optional warn level for the operation. Possible values are `WARN` and `NONE`.
Example usage: `ib object -n network update --schedule-warn-level=WARN ...`

- `--approval-comment`: optional comment for the approval operation. Example usage:
`ib object -n network create --approval-comment='a comment' ...`

- `--approval-query-mode`: optional query mode for the approval operation. Possible values are `true` and `false`.
Example usage: `ib object -n network update --approval-query-mode=true ...`

- `--approval-ticket-number`: optional ticket number for the approval operation. Example usage:
`ib object -n network update --approval-ticket-number=11898 ...`

- `--return-fields`: comma-separated list of fields to be returned to check the updated object.
Example usage: `ib object -n network update --return-fields=comment,utilization ...`

- `--return-fields-plus`: comma-separated list of fields to be returned in addition of the basic fields to check the
updated object. Example usage: `ib object -n network update --return-fields-plus=netmask,utilization ...`

- `-a, --arguments`: a json string representing arguments to pass to the update command. Example usage:
`ib object -n network update -a '{"comment":"a new comment"}'`

### `delete`

This command deletes an infoblox object given its reference.

Options:

- `-o, --object-ref`: reference of the infoblox object to delete. Example usage:
`ib object -n network delete -o object-reference`

- `--schedule-time`: optional timestamp representing the date to perform the operation. Example usage:
`ib object -n network delete --schedule-time=1599688800 ...`

- `--schedule-now`: optional boolean to execute the operation at the current time. You should set this option **only if
you don't use** option `--schedule-time`. Example usage: `ib object -n network delete --schedule-now=yes ...`

- `--schedule-predecessor-task`: optional reference to a scheduled task that will be executed before the submitted task.
Example usage: `ib object -n network delete --schedule-predecessor-task=task-reference ...`

- `--schedule-warn-level`: optional warn level for the operation. Possible values are `WARN` and `NONE`.
Example usage: `ib object -n network delete --schedule-warn-level=WARN ...`

- `--approval-comment`: optional comment for the approval operation. Example usage:
`ib object -n network delete --approval-comment='a comment' ...`

- `--approval-query-mode`: optional query mode for the approval operation. Possible values are `true` and `false`.
Example usage: `ib object -n network delete --approval-query-mode=true ...`

- `--approval-ticket-number`: optional ticket number for the approval operation. Example usage:
`ib object -n network delete --approval-ticket-number=11898 ...`
