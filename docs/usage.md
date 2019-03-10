# Usage

[TOC]

We will show how to use the client and the CLI by performing the same operations with both. This tutorial is mainly
inspired by the wapidoc [tutorial](https://ipam.illinois.edu/wapidoc/additional/sample.html).

## Instantiate a client

To instantiate a new client you will need to perform the following command:

````python
from infoblox import Client

client = Client(url='https://foo.com/wapi/v2.8', user='foo', password='foo')
````

!!! note
    You can define three environment variables `IB_URL`, `IB_USER` and `IB_PASSWORD` and later instantiate the client
    without using keyword parameters like this `client = Client()`
    
!!! note
    If you have a `.env` file with configured environment variables, you can instantiate the client as follows:
    `client = Client(dot_env_path=path_to_env_file)`

!!! note
    If you have configured a client certificate, you can pass the path of the `.pem` file or a tuple
    `(certificate_file, private_key)` to the `cert` keyword argument of the `Client` class like this:
    `client = Client(cert=path_to_pem_file)` or `client = Client(cert=(path_to_certificate_file, path_to_private_key))`

## Configure the CLI

The CLI included with the project is called `ib`. To use it, you will have to configure the following environment
variables:

- **IB_USER:** the user to connect to
- **IB_PASSWORD:** the user's password
- **IB_URL:** the wapi url which must be of the form `https://foo.com/wapi/v2.X`

To not repeat yourself every time you need to use the CLI, you can create a `.env` file with the above environment
variables and put it in your working directory. `ib` command will automatically load this file so you can focus on
performing tasks.

!!! note
    you can activate shell completion by performing the command `ib shell-completion`. This will only work on `bash`,
    `fish`, `zsh` and `PowerShell`

To know more about configuring the CLI, you can check the [CLI](cli.md) page.

## Performing actions

### Create a network

Using the client:

````python
network = client.get_object('network')
network.create(network='10.1.0.0/16')
````

Using the CLI:

````console
ib object -n network create -a '{"network":"10.1.0.0/16"}'
````

**N.B:** On PowerShell you will need to use a different syntax to encode properly json string. In the rest of the
tutorial, we will use the *bash*-like syntax.

````console
ib object -n network create -a "{\"network\":\"10.1.0.0/16\"}"
````

!!! note
    To know all options and sub-commands available within a command, you can use the `-h` option.

The response will contain the reference of the created network:

````console
"network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16"
````

### Read a network

Using the client:

````python
network.get()
````

using the CLI:

```console
ib object -n network get
```

You will get an output similar to this:

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

!!! note
    All responses are returned in `json` format, there is no `xml` supported

### Modify a network

Using the client:

```python
network.update(object_ref='network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0/16', comment='just a comment')
```

using the CLI:

```console
ib object -n network update -o network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16 -a '{"comment":"just a comment"}'
```

The response will contain the reference of the modified network. This could be different from the created one.

`````console
"network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16"
`````

To check if the network was modified, we will search it. Note the usage of `return_fields` parameter to specify which
fields to return.

Using the client:

````python
network.get(return_fields=['network', 'networkview', 'comment'])
````

using the CLI:

```console
ib object -n network get --return-fields=network,networkview,comment
```

Note that the 10.1.0.0/16 network has been modified:

````json
[
    {
        "_ref": "network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16",
        "comment": "just a comment",
        "network": "10.1.0.0/16",
        "network_view": "default"
    },
    {
        "_ref": "network/ZG5zLm5ldHdvcmskMTAuMi4wLjAvMTYvMA:10.2.0.0%2F16",
        "network": "10.2.0.0/16",
        "network_view": "default"
    }
]
````

### Search for a network

To search for networks with comments that contain the word *just* in a case-insensitive way, we can perform the
following operations.

Using the client:

```python
network.get(params={'comment~:': 'just'})
```

using the CLI:

```console
ib object -n network get -p '{"comment~:":"just"}'
```

You will have an empty list in response if there is no matching or a response similar to this:

````json
[
    {
        "_ref": "network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16",
        "comment": "just a comment",
        "network": "10.1.0.0/16",
        "network_view": "default"
    }
]
````

### Delete a network

Using the client:

```python
network.delete(object_ref='network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0/16')
```

using the CLI:

```console
ib object -n network delete -o network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16
```

The reference of the deleted network will be returned:

````console
"network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0%2F16"
````

### Create a host record

To create a host record, we will first need to create a zone.

using the client:

````python
zone_auth = client.get_object('zone_auth')
zone_auth.create(fqdn='zone.com')
````

using the CLI:

````console
ib object -n zone_auth create -a '{"fqdn":"zone.com"}'
````

Then now we can create a host.

using the client:

````python
record_host = client.get_object('record:host')
record_host.create(ipv4addrs=[{'ipv4addr':'10.222.0.12'}], name='host.zone.com')
````

using the CLI:

````console
ib object -n record:host create -a '{"ipv4addrs":[{"ipv4addr":"10.222.0.12"}],"name":"host.zone.com"}'
````

### Schedule an object creation

Using the client:

There is a keyword argument `schedule_time` which comes in handy to schedule an object creation.

````python
network = client.get_object('network')
network.create(schedule_time=1367752903, network='10.1.0.0/16')
````

using the CLI:

There is an option `--schedule-time` that can be used with the `create` command.

````console
ib object -n network create -a '{"network":"10.1.0.0/16"}' --schedule-time=1367752903
````

The response will contain the reference of the created scheduled task

````console
"scheduledtask/b25lLnF1ZXVlZF90YXNrJDY:6/PENDING"
````

### Execute a function call

Using the client:

There is a handy method `func_call` that helps to realize function calls easily. Admitting we have created the network
`10.1.0.0/16` with the previous operation and we have its reference, we can do this to get the three next available
/24 networks excluding `10.1.1.0/24` and `10.1.3.0/24`

````python
network = client.get_object('network')
network.func_call(object_ref='network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0/16/default',
function_name='next_available_network', exclude=['10.1.1.0/24', '10.1.3.0/24'], cidr=24, num=3)
````

using the CLI:

There is an `object` sub-command `func-call` which allows the same operation to be performed as above.

````console
ib object -n network func-call -o network/ZG5zLm5ldHdvcmskMTAuMS4wLjAvMTYvMA:10.1.0.0/16/default -n next_available_network\
-a '{"exclude":["10.1.1.0/24","10.1.3.0/24"],"cidr":24,"num":3}'
````

You will get something similar to the following:

````console
{
    "networks": [
            "10.1.0.0/24",
            "10.1.2.0/24",
            "10.1.4.0/24"
        ]
}
````

### Upload a file to the appliance

To upload a file to the appliance, we first need to warn him.

Using the client:

````python
file_op = client.get_object('fileop')
file_op.func_call(function_name='uploadinit')
````

using the CLI:

````console
ib object -n fileop func-call -n uploadinit -a '{}'
````

Note that even if the function does not take an argument you need the provide an *empty json*, otherwise you will get
an error.

The appliance will return an url where to upload the file and a token value like following:

````json
{
    "token": "eJydkMFOwzAMhu9+k......",
    "url": "https://192.168.1.2/...."
}
````

The file can then be uploaded to the specified url. For that we will use the underlying 
[requests.Session](http://docs.python-requests.org/en/master/user/advanced/#session-objects) object used by our client
instance since there is no particular method dedicated to upload files.

Using the client:

````python
session = client.session
files = {'import_file': open('foo.txt', 'rb')}
session.post('https://192.168.1.2/....', files=files)
````

using the CLI:

`ib` CLI utility does not have a native command to upload or download files since it is not his main purpose. You will
need another CLI utility to perform those actions. Two good options are [curl](https://curl.haxx.se/) and
[httpie](https://httpie.org/). You can install the latter with the following command (assuming you have pip installed):

````console
pip install httpie
````

We will use it th show how to handle files. To perform the previous action, just type this:

````console
http --verify=no -a username:password -f POST https://192.168.1.2/... import_file@foo.txt 
````

!!! note
    In the previous example, the filename is *import_file* because we did not specify any filename when performing
    the action `upload_init` like as stated in the
    [documentation](https://ipam.illinois.edu/wapidoc/objects/fileop.html#uploadinit)

To better understand the syntax, you can take a look at httpie [documentation](https://httpie.org/doc).

Finally, we need to signal the appliance that the upload has been completed and that it needs to perform the
requested action on the uploaded file. In this example, we will use
[setfiledest](https://ipam.illinois.edu/wapidoc/objects/fileop.html#upload-setfiledest).

using the client:

````python
file_op = client.get_object('fileop')
file_op.func_call(function_name='setfiledest', dest_path='/foo.txt', type='TFTP_FILE', token='eJydkMFOwzAMhu9+k...')
````

using the CLI:

````console
ib object -n fileop func-call -n setdestfile -a '{"dest_path":"/foo.txt","type":"TFTP_FILE","token":"eJydkMFOwzAMhu9+k..."}'
````

### Download a file from the appliance

To download a file from the appliance, we first need to select what to download, in this example it will be a backup.

Using the client:

````python
file_op = client.get_object('fileop')
file_op.func_call(function_name='getgriddata', type='backup')
````

using the CLI:

````console
ib object -n fileop func-call -n getgriddata -a '{"type":"backup"}'
````

The appliance will return a token and a URL from which the file should be downloaded:

````json
{
    "token": "eJydUMtuwyAQvO....",
    "url": "https://192.168.1.2/...."
}
````

Now we can download the file.

Using the client:

````python
session = client.session
r = session.get('https://192.168.1.2/....', stream=True)
with open('foo.txt', 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)
````

using httpie CLI:

````console
http --verify=no -a username:password --download https://192.168.1.2/....
````

After the download has been completed, we can signal the appliance that the operation is done by calling
[downloadcomplete](https://ipam.illinois.edu/wapidoc/objects/fileop.html#downloadcomplete) and passing the token
we have retrieved in the first step.

Using the client:

````python
file_op = client.get_object('fileop')
file_op.func_call(function_name='downloadcomplete', token='eJydUMtuwyAQvO....')
````

using the CLI:

````console
ib object -n fileop func-call -n downloadcomplete -a '{"token":"eJydUMtuwyAQvO...."}'
````

### Retrieve a lot of data

If you want to retrieve hundreds or thousands of objects in one call, the client method `get` is not suitable. There
is a more convenient method `get_multiple` which takes care to not need a lot of memory to retrieve objects. It's usage
is quite simple:

````python
network = client.get_object('network')
for net in network.get_multiple(params={'network_view': 'default'}):
    print(net)  # do whatever you want with the retrieved network
````

**There is no equivalent for the CLI**

Also, if you just need to count a set of objects matching specific rules, there is a handy method `count` that you
can used.

Using the client:

````python
network = client.get_object('network')
network.count(params={'network_view': 'default', 'comment~': 'sample'})
````

using the CLI:

````console
ib object -n network count -p '{"network_view":"default","comment~":"sample"}'
````

### Execute a custom request

One specificity of infoblox api is to perform many actions in one HTTP call. It is done via the
[request](https://ipam.illinois.edu/wapidoc/objects/request.html) object. With *ib-client* you can perform the same
thing by using the client `custom_request` method or the `request` sub command if you use the CLI. We will take one
example of this [tutorial](https://ipam.illinois.edu/wapidoc/additional/samplebodyrequests.html) which consists
of getting a host record with the name *test.somewhere.com*, saved its reference to the state object and used it for an
update operation.

Using the client:

````python
data = [
    {
        "method": "STATE:ASSIGN",
        "data": {
            "host_name": "test.somewhere.com"
        }
    },
    {
        "method": "GET",
        "object": "record:host",
        "data": {
            "name": "##STATE:host_name:##"
        },
        "assign_state": {
            "host_ref": "_ref"
        },
        "enable_substitution": True,
        "discard": True
    },
    {
        "method": "PUT",
        "object": "##STATE:host_ref:##",
        "enable_substitution": True,
        "data": {
            "comment": "new comment"
        },
        "args": {
            "_return_fields": "comment"
        },
        "assign_state": {
            "updated_comment": "comment"
        },
        "discard": True
    },
    {
        "method": "STATE:DISPLAY"
    }
]

client.custom_request(data)
````

Simple enough! The hardest part is to know how to format your request.

Using the CLI:

````console
ib request '[{"method":"STATE:ASSIGN","data":{"host_name":"test.somewhere.com"}},{"method":"GET","object":"record:host",\
"data":{"name":"##STATE:host_name:##"},"assign_state":{"host_ref": "_ref"},"enable_substitution": true,"discard": true},\
{"method":"PUT","object":"##STATE:host_ref:##","enable_substitution": true,"data":{"comment":"new comment"},"args":\
{"_return_fields":"comment"},"assign_state":{"updated_comment":"comment"},"discard":true},{"method":"STATE:DISPLAY"}]'
````

Like you see, it is definitely not convenient to perform your operation this way. This is why the command accepts a `-j`
option where you can pass the path of a **json** file which contains the body of the request. Assuming you have a json
file `foo.json` in your working directory with this content:

````json
[{
    "method": "STATE:ASSIGN",
    "data": {
            "host_name": "test.somewhere.com"
    }
},
{
    "method": "GET",
    "object": "record:host",
    "data": {
            "name": "##STATE:host_name:##"
    },
    "assign_state": {
                    "host_ref": "_ref"
    },
    "enable_substitution": true,
    "discard": true
 },
 {
    "method": "PUT",
    "object": "##STATE:host_ref:##",
    "enable_substitution": true,
    "data": {
            "comment": "new comment"
    },
    "args": {
        "_return_fields": "comment"
    },
    "assign_state": {
                    "updated_comment": "comment"
    },
    "discard": true
 },
 {
    "method": "STATE:DISPLAY"
 }
]
````

You can run this command instead:

````console
ib request -j foo.json
````

Simple enough! The result of this request will look like the following:

````json
{
     "host_name": "test.somewhere.com",
     "host_ref": "record:host/ZG5...zdA:test.somewhere.com/default",
     "updated_comment": "new comment"
}
````