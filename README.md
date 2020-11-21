# TunnelPy

### Table of Contents
- **[Introduction](#introduction)**
- **[Detailed info](#detailed-info)**
- **[Usage examples](#usage-examples)**
- **[Author](#author)**
- **[Known issues](#known-issues)**

### Introduction
TunnelPy simply exposes any service, running internally in a network/host, to the outside.

This it does by binding a socket to a port on a mhost, such that the mhost:mport ('middle-man host and port') is accessible from 'outside the network', and every request sent to this socket is relayed to your chosen dhost:dport (destination host and port), and any reply from there is relayed back to the client.

### Detailed info
You can run this script on any host that you'd like to use as the middle-man, and choose a port on the host that is allowed by the firewall to the outside, and you can then simply use this mport on the middle-man host to forward your data to any chosen dhost:dport connected to the middle-man host, INCLUDING (obviously) the same host itself.

In other words, mport (middle-man's port) will be available for you to send data to/receive data from, and it'd act as if you sent/received the data to/from dhost:dport (destination host's ip and port). This makes a data tunnel between the client, the TunnelPy server as the middle-man, and the dhost:dport.

Also, the TunnelPy server uses threading, so you can send multiple requests, and each one of them will be handled completely in an entire new thread of its own.

**Arguments:**
```
--tunnel      : Precede the tunnelpy host and port arguments by this
                Format: --tunnel <mport>:<dhost ip>:<dport>
--verbose, -v : Start the tunnelpy server in verbose mode (shows the data in transit)
--quiet, -q   : Start the tunnelpy server in quiet mode (shows no transit information)
--timeout, -t : Set the global timeout for receiving data (default: 1 second)
--help, -h    : Get this help message
--examples    : See some usage examples
```

### Usage examples

- **Example 1:**
Say you are at 10.0.0.3, and 10.0.0.8 has an internal service running on its loopback interface on port 7878. You want to have this service exposed on its accessible interface on port 4444.

  For this, you execute the script on 10.0.0.8 as:
  ```
  tunnel.py -v --tunnel 4444:127.0.0.1:7878
  ```

  This will establish a tunnel between **10.0.0.8:4444 <--> 127.0.0.1:7878**, and you can communicate with 10.0.0.8:4444 to actually talk to 127.0.0.1:7878.
  
  Do note that you will also see the request and response data in transit because of '-v'. Also, default timeout of 1 second is used, since '-t' is not used.


- **Example 2:**
  Say you are at 10.0.0.3, and 10.0.0.8 is allowed by firewall to access a service running on port 7878 of another host 10.0.0.16 (connected to 10.0.0.8), but you are not. You can only access 10.0.0.8. You cannot directly access this from 10.0.0.3, but using 10.0.0.8 as the middle-man, you can. Say you want to have this service exposed on 10.0.0.8:4444.

  For this, you execute the script on 10.0.0.8 as:
  ```
  tunnel.py -t 3 --tunnel 4444:10.0.0.16:7878
  ```
  This will establish a tunnel between **10.0.0.8:4444 <--> 10.0.0.16:7878**, and you can communicate with 10.0.0.8:4444 to actually talk to 10.0.0.16:7878.

  Do note that the timeout for all receive operations is explicitly set to 3 seconds here.

### Author
CaptainWoof

**Twitter:** [@realCaptainWoof](https://twitter.com/realCaptainWoof)

### Known issues
- **Q: Why does HTTP requests fail when using the URL with hostname/domain name in as `dhost`?**

  **A:** I have seen errors happening sometimes when such URLs are used. It is most probably an issue of the tunnel only tunneling between the specified ports, which means that there is nothing that resolves the hostname (DNS).

  **Fix:** If you see errors, use the IP address of the destination host in 'dhost' instead of the name. Alternatively, you can try using tunnelpy to tunnel your DNS requests as well, though *this has not yet been tested*.

