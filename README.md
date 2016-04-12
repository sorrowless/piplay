**Piplay** is a small console player which can play music from several online
sources (they named *storages* in terminology of Piplay). Currrently supported:

* VK
* YouTube

Piplay is written as client/server software, so you have a server which get
requests and transform them into queries to search and manage playing process.
It is pretty small software (at current moment it is <1000 SLOC of python),
written more or less on non-blocking socket principles.

Internal architecture splits to 2 main parts: *server* and *client*.

*Server* part splits into server daemon which accept requests, manager which
handles those requests, storages which process queries and player that plays
a results.

*Client* part can make a requests to server.


**Usage**:

If you use storages that needs explicit acess to API, you should have a config
file with needed access. Config file is an ini-style file divided to sections
with keys. Config file must be placed at '~/.piplay/config' and be readable to
piplay.

*VK storage settings*:
To access VK db you must have special 'application' which created to make API
calls to VK db. Also you must have an account in vk.com
That 'application' has an ID. To get it you must first of all create a new
'application' instance via [0] link. After creation there will be ID shown in
'settings' link. Then you should add section 'vk' into config file like below:

```

  [vk]
  app_id = <application ID>
  user_login = <your login in vk.com>
  user_password = <your password in vk.com>

```

After this piplay will have an access to VK db.

*YouTube storage settings*:
To access YouTube db you also should hav an application ID. To get it, follow
instructions from [1]. You must have google account to to that. After getting
application key for YouTube, place it into config file like this:

```

  [youtube]
  app_key = <application key>

```

After this piplay will have an access to YouTube db.

*Common settings*
You can change some other settings:

* notifications: create a next key in 'common' section:

```

  [common]
  notifications = true

```

  to get working notifications. You need python bindings for DBUS to see them,
  btw - and you usually need to install this package manually, as it is not
  pure Python one and doesn't shipped by pip. In different systems it can be
  named different way, there is examples for most popular distributes:

  1. Arch: python-dbus
  2. Ubuntu: python3-dbus


**Roadmap**:

* add more storages: local, torrent, pleer.com and so on
* implement full more requests: pause, retry, play random, resume
* move from pure non-blocked sockets to HTTP-based ones


**License**:

There is no license files and/or headers in this software, so it is exclusive
and you need to ask author if you want to use this software any way for getting
money. But you can freely use it in open-source projects without any payments.


[0] https://vk.com/apps?act=manage

[1] https://console.cloud.google.com/apis/api/youtube/overview
