# API

[TOC]

## Client

A `Client` class is the base class provided by *ib-client* package to interact with an infoblox API.

### Initialization

The following *optional* keyword arguments are available when instantiating the class:

- `url`: The url to connect to the infoblox API which must be of the form `http://<host>/wapi/v2.X`.
- `user`: The user to connect to. It is used in the process of **HTTP Basic Authentication**.
- `password`: The user's password. It is used in the process of **HTTP Basic Authentication**.
- `cert`: The path to the client certificate if you have one for your API server. The value of this parameter has two
forms. The first is to provide the path of the `pem` file, the second is to provide a tuple of paths
(certificate_file_path, private_key_path).
- `dot_env_path`: Like the parameter name suggests, it is the path to a `.env` file that will be used to configure
the url, user and password. It is an alternate way to provide the parameters `url`, `user` and `password`. The 3
minimum information required in this file are `IB_URL`, `IB_USER` and `IB_PASSWORD`. Note that if you provide this 
parameter with the first three, the latter will take precedence.

### `api_schema`

This property returns the infoblox API schema.

### `available objects`

This property returns all available infoblox objects in the current version of API.

### `session`

This property returns the underlying
[requests.Session](http://docs.python-requests.org/en/master/user/advanced/#session-objects) used to perform
HTTP requests. It is useful when performing [upload](usage.md#upload-a-file-to-the-appliance) or
[download](usage.md#download-a-file-from-the-appliance) operations.

!!! note
    In the following methods, the annotation `Json` represents type hint `Union[dict, str, list]`.

### `custom_request()`

Signature: `custom_request(data: Json = None) -> Json`

This method allows you to perform [custom requests](usage.md#execute-a-custom-request).

Parameter:

`data`: The body of the request.

### `get_object()`

Signature: `get_object(name: str) -> Resource`

This methods returns a [resource](#resource) object that you can use to interact with infoblox objects of the type
which name is passed as argument.

Parameter:

`name`: The name of the infoblox object e.g *record:host* or *network*.

## Resource

This class helps to interact with infoblox objects. Normally you don't have to interact directly with this class, but
you will get an instance via the client method [get_object](#get_object). Note that all the CRUD operations are possible
with this class.

### `documentation`

This property returns the API documentation of the object. It gives all the information necessary to interact with 
objects of the concerned type.

### `name`

This property returns the name of the concerned infoblox object.

### `fields`

This property returns the list of fields available for the concerned infoblox object. Even **search-only fields** are listed.

### `functions`

This property returns the list of all available functions of the concerned infoblox object. It may be empty if the
concerned infoblox object does not offer functions.

### `get_field_information()`

Signature: `get_field_information(name: str) -> dict`

This method returns information about a field of the concerned infoblox object. You will have information about its
type, how you can use it with search modifiers to filter results, etc...

Parameter:

`name`: The name of the field to probe.

### `get_function_information()`

Signature: `get_function_information(name: str) -> dict`

This method returns information about a function of the concerned infoblox object. You will know input parameters that the
function takes and what output information is expected.

Parameter:

`name`: The name of the function to probe.

### `get()`

Signature: `get(object_ref: str = None, params: dict = None, return_fields: List[str] = None, return_fields_plus: List[str] = None, proxy_search: str = None) -> Json`

This method retrieves objects. It is indicated to use this method when you want to get a specific object or just a few
of them. If you want to retrieve a lot of objects (hundreds or thousand or more..), please refer to
[get_multiple](#get_multiple) method.

Parameters:

- `object_ref`: the reference of the object to get.
- `params`: a dict with parameters that helps you to filter the results. Note that search modifiers can be used to
refine conditions. For example, assuming we are manipulating
[network](https://ipam.illinois.edu/wapidoc/objects/network.html) resources, we can filter objects to return with
these conditions: `params={'comment~': 'gateway', 'network_view!': 'default'}`.
- `return_fields`: the list of fields to return within objects. If you don't provide this parameter, you will get the
basic fields of the concerned object.
- `return_fields_plus`: the list of fields to return in addition of the basic fields of the concerned object.
- `proxy_search`: the values possible are **GM** to redirect requests to Grid master for processing or **LOCAL** to 
process locally. This option is applicable only on vConnector grid members. If you don't provide this parameter, the
default will be **LOCAL**.

### `get_multiple()`

Signature: `get_multiple(params: dict = None, return_fields: List[str] = None, return_fields_plus: List[str] = None, proxy_search: str = None) -> Iterator[dict]`

This method helps to retrieve lot of objects without exploding the memory used.

Parameters:

- `params`: a dict with parameters that helps you to filter the results. Note that search modifiers can be used to
refine conditions. For example, assuming we are manipulating
[network](https://ipam.illinois.edu/wapidoc/objects/network.html) resources, we can filter objects to return with
these conditions: `params={'comment~': 'gateway', 'network_view!': 'default'}`.
- `return_fields`: the list of fields to return within objects. If you don't provide this parameter, you will get the
basic fields of the concerned object.
- `return_fields_plus`: the list of fields to return in addition of the basic fields of the concerned object.
- `proxy_search`: the values possible are **GM** to redirect requests to Grid master for processing or **LOCAL** to 
process locally. This option is applicable only on vConnector grid members. If you don't provide this parameter, the
default will be **LOCAL**.

### `count()`

Signature: `count(params: dict = None, proxy_search: str = None) -> int`

This method comes in handy when you just want to count specific objects without retrieving them.

Parameters:

- `params`: a dict with parameters that helps you to filter the results. Note that search modifiers can be used to
refine conditions. For example, assuming we are manipulating
[network](https://ipam.illinois.edu/wapidoc/objects/network.html) resources, we can filter objects to return with
these conditions: `params={'comment~': 'gateway', 'network_view!': 'default'}`
- `proxy_search`: the values possible are **GM** to redirect requests to Grid master for processing or **LOCAL** to 
process locally. This option is applicable only on vConnector grid members. If you don't provide this parameter, the
default will be **LOCAL**.

### `create()`

Signature: `create(schedule_time: int = None, schedule_now: bool = False, schedule_predecessor_task: str = None, schedule_warn_level: str = None, approval_comment: str = None, approval_query_mode: str = None, approval_ticket_number: int = None, return_fields: List[str] = None, return_fields_plus: List[str] = None, **kwargs) -> Json`

As the name of the method states, this method performs creation of infoblox objects.

Parameters:

- `schedule_time`: timestamp representing the date to perform the operation.
- `schedule_now`: indicates whether to perform the operation now or not. This parameter cannot be used at the same time
as the `schedule_time` parameter.
- `schedule_predecessor_task`: reference to a scheduled task that will be executed before the submitted task.
- `schedule_warn_level`: warn level for the operation. Valid values are **WARN** and **NONE**. If not provided, **NONE**
will be used.
- `approval_comment`: comment for the approval operation. It can be required or optional depending of the settings of
your approval workflow.
- `approval_query_mode`: query mode for the approval operation. Valid values are `"true"` and `"false"`. If not provided
the default value is `"false"`.
- `approval_ticket_number`: ticket number for the approval operation.
- `return_fields`: the list of fields to return in the response of the creation operation. If not provided, only the
**reference** of the created object will be returned.
- `return_fields_plus`: the list of fields to return in addition of the basic fields in the response of the creation
operation. If not provided, `return_fields` will be returned if provided otherwise, only the reference of the created
object will be returned.
- `kwargs`: various fields to pass as keyword arguments to create an object. For example to create a network, you can 
do this `create(network='192.168.1.0/24', comment='first network')`.

### `update()`

Signature: `update(self, object_ref: str = None, schedule_time: int = None, schedule_now: bool = False, schedule_predecessor_task: str = None, schedule_warn_level: str = None, approval_comment: str = None, approval_query_mode: str = None, approval_ticket_number: int = None, return_fields: List[str] = None, return_fields_plus: List[str] = None, **kwargs) -> Json:`

This method updates an object by giving its reference as input.

Parameters:

- `object_ref`: reference of the object to update.
- `schedule_time`: timestamp representing the date to perform the operation.
- `schedule_now`: indicates whether to perform the operation now or not. This parameter cannot be used at the same time
as the `schedule_time` parameter.
- `schedule_predecessor_task`: reference to a scheduled task that will be executed before the submitted task.
- `schedule_warn_level`: warn level for the operation. Valid values are **WARN** and **NONE**. If not provided, **NONE**
will be used.
- `approval_comment`: comment for the approval operation. It can be required or optional depending of the settings of
your approval workflow.
- `approval_query_mode`: query mode for the approval operation. Valid values are `"true"` and `"false"`. If not provided
the default value is `"false"`.
- `approval_ticket_number`: ticket number for the approval operation.
- `return_fields`: the list of fields to return in the response of the update operation. If not provided, only the
**reference** of the updated object will be returned.
- `return_fields_plus`: the list of fields to return in addition of the basic fields in the response of the update
operation. If not provided, `return_fields` will be returned if provided otherwise, only the reference of the updated
object will be returned.
- `kwargs`: various fields to pass as keyword arguments to update an object. For example to update a network with
 reference *my-ref* you can do this `update(object_ref='my-ref', comment='new comment')`.
 
### `delete()`

Signature: `delete(self, object_ref: str = None, schedule_time: int = None, schedule_now: bool = False, schedule_predecessor_task: str = None, schedule_warn_level: str = None, approval_comment: str = None, approval_query_mode: str = None, approval_ticket_number: int = None) -> Json`

This method deletes an object by giving its reference as input.

Parameters:

- `object_ref`: reference of the object to delete.
- `schedule_time`: timestamp representing the date to perform the operation.
- `schedule_now`: indicates whether to perform the operation now or not. This parameter cannot be used at the same time
as the `schedule_time` parameter.
- `schedule_predecessor_task`: reference to a scheduled task that will be executed before the submitted task.
- `schedule_warn_level`: warn level for the operation. Valid values are **WARN** and **NONE**. If not provided, **NONE**
will be used.
- `approval_comment`: comment for the approval operation. It can be required or optional depending of the settings of
your approval workflow.
- `approval_query_mode`: query mode for the approval operation. Valid values are `"true"` and `"false"`. If not provided
the default value is `"false"`.
- `approval_ticket_number`: ticket number for the approval operation.


### `func_call()`

Signature: `func_call(self, object_ref: str = None, function_name: str = None, **kwargs) -> Json`

This function performs a function call on an object. It returns information about the result of the operation.

Parameters:

- `object_ref`: optional reference of the object to which the function is to be applied.
- `function_name`: the name of the function to call.
- `kwargs`: keyword arguments representing input parameters of the function.