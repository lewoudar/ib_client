# ib-client

[![Pypi version](https://img.shields.io/pypi/v/ib-client.svg)](https://pypi.org/project/ib-client/)
[![Build Status](https://travis-ci.com/lewoudar/ib_client.svg?branch=master)](https://travis-ci.com/lewoudar/ib_client)
[![Windows Build Status](https://img.shields.io/appveyor/ci/lewoudar/ib-client/master.svg?label=Windows)](https://ci.appveyor.com/project/lewoudar/ib-client)
[![Coverage Status](https://codecov.io/gh/lewoudar/ib_client/branch/master/graphs/badge.svg?branch=master&token=J6NUl2epJX)](https://codecov.io/gh/lewoudar/ib_client)
[![Documentation Status](https://readthedocs.org/projects/ib-client/badge/?version=latest)](https://ib-client.readthedocs.io/en/latest/?badge=latest)
[![License Apache 2](https://img.shields.io/hexpm/l/plug.svg)](http://www.apache.org/licenses/LICENSE-2.0)

The simplest infoblox client!

## Why another infoblox client?

This may be the first question that come to your mind if you know that there is already 
a [client](https://infoblox-client.readthedocs.io/en/stable/) supported by Infoblox.
 
The answer is **genericity**. I try to be the more generic as possible to support all the objects proposed by the 
infoblox API through the instropection of its API. If you know the [wapi](https://ipam.illinois.edu/wapidoc)
documentation of an object / function, you will know how to use through the client which has a *simple* and
*intuitive* API.

## Installation

```bash
pip install ib-client
```

**N.B: ib-client works starting from python 3.6**

## Documentation

The documentation is available at https://ib-client.readthedocs.io/en/stable/.

## Features

- A client that allows you to perform all the operations available in the infoblox api.
- A CLI that allows you to quickly perform the same operations as you will do with the client.
- Ability to perform custom 
[requests](https://ipam.illinois.edu/wapidoc/additional/samplebodyrequests.html#samplebody-single).
- Ability to load `.env` files to configure the client or the CLI.


## Usage

### Client

Here is how you can instantiate the client.

````python
from infoblox import Client

client = Client(url='https://foo.com/wapi/v2.8', user='foo', password='foo')
````

To create a network:

```python
network = client.get_object('network')
network.create(network='10.1.0.0/16')
```

To read all networks created:

```python
network.get()
```

You will have an output similar to the following:

```json
[
    {
        "_ref": "network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16",
        "network": "10.1.0.0/16",
        "network_view": "default"
    },
    {
        "_ref": "network/ZG5zLm5ldHdvcmskMTAuMi4wLjAvMTYvMA:10.2.0.0%2F16",
        "network": "10.2.0.0/16",
        "network_view": "default"
    }
]
```

To modify a network:

```python
network.update(object_ref='network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0/16', comment='just a comment')
```

If you want to search for the network modified, you can do this:

```python
network.get(params={'comment~': 'just'}, return_fields=['network', 'networkview', 'comment'])
```

It is also interesting to notice in the last call how we filtered the fields to be returned. The output contains the
network modified previously.

```json
[
    {
        "_ref": "network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16",
        "comment": "just a comment",
        "network": "10.1.0.0/16",
        "network_view": "default"
    }
]
```

**N.B:** the reference is always returned, so this is why we don't need to mention it in the `return_fields` parameter.

Finally to delete a network, you can perform this call:

```python
network.delete(object_ref='network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0/16')
```

Simple enough!

### CLI

Before using the CLI, you will have to set 3 environment variables, otherwise you will have an error. The 3 environment
variables are:
- **IB_URL:** the wapi infoblox url like https://foo/wapi/v2.8
- **IB_USER:** the user to connect to
- **IB_PASSWORD:** the user's password

If you don't want to repeat these actions, you can create a **.env** file in the directory where you want to use the CLI.
You need to provide the above information in the form `KEY=VALUE`, one per line.

The cli has *help information* available to help you quickly understand how to use it

```bash
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
```

Each command also has help information available through the `-h` option.
You can activate the shell completion on **bash**, **fish**, **zsh** and **Powershell** by doing the following command:

```bash
ib shell-completion
```

**Note:** On Powershell, you may encounter an error in non administrator mode and if you are in administrator mode,
and you still encounter an error like the following:

```bash
Set-ExecutionPolicy : Windows PowerShell updated your execution policy successfully, but the setting is overridden
by a policy defined at a more specific scope.  Due to the override, your shell will retain its current effective
execution policy of Bypass. Type "Get-ExecutionPolicy -List" to view your execution policy settings.
For more information please see "Get-Help Set-ExecutionPolicy".
```

Please refer to [microsoft documentation](http://go.microsoft.com/fwlink/?LinkId=821719) to know how to fix the issue.

We will now perform the same operations realized in the client part.

Create a network:

```bash
ib object -n network create -a '{"network": "10.1.0.0/16"}'
```

Notes: 
- the `-n` option after `object` command specifies the object to work on.
- On Powershell, you will need a different syntax to escape properly json arguments:

```bash
ib object -n network create -a "{\"network\": \"10.1.0.0/16\"}"
```

I know it is ugly and tricky, but we can't do differently on Windows :(

To get all created networks:

```bash
ib object -n network get
```

Update a network:

```bash
ib object -n network update -o network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16 -a '{"comment":"just a comment"}'
```

Search for a network:

```bash
ib object -n network get -p '{"comment~":"just"}' --return-fields=network,networkview,comment
```

Delete a network:

```bash
ib object -n network delete -o network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16
```

# Warnings

- The client was created by working on major version 2 of the infoblox API, so it is sure to work on it, will not work
 on a previous major version and is not sure to work on a higher major version.
- I don't have much time to test my client on an infoblox server, so it's likely there are some bugs. Feel free to suggest
pull requests. See the CONTRIBUTING.md file for more details. All contributions are welcome :)