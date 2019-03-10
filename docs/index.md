# ib-client documentation

Everything you need to know about ib-client.


## Why another infoblox client?

This may be the first question that come to your mind if you know that there is already 
a [client](https://infoblox-client.readthedocs.io/en/stable/) supported by Infoblox.
 
The answer is **genericity**. I try to be the more generic as possible to support all the objects proposed by the 
infoblox API through the instropection of the latter. If you know the [wapi](https://ipam.illinois.edu/wapidoc)
documentation of an object / function, you will know how to use through the client which has a *simple* and
*intuitive* API.

## Features

- A client that allows you to perform all the operations available in the infoblox api.
- A CLI that allows you to quickly perform the same operations as you will do with the client.
- Ability to perform custom 
[requests](usage.md#perform-a-custom-request).
- Ability to load `.env` files to configure the client or the CLI.

## Contents

- [Installation](installation.md)
- [Usage](usage.md)
- [API](api.md)
- [CLI](cli.md)
- [Changelog](changelog.md)