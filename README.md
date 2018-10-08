# sRequests
Simple Python 3 library to make HTTP requests. Based on socket.

# About
sRequest - simple library to make HTTP requests fully based on socket. In theory must work on all platforms by default.
Inspired by [Requests](https://github.com/requests/requests)


- Based on default Python library
- SSL/TSL support
- Custom headers support
- HTTP 1.0 protocol in use
- Have history of redirects
- Objects:

   - redirects - count of redirects in requests
   - url - current url
   - status_code - returned status code (full, not only code)
   - headers - response headers
   - con_header - request headers
   - history - contains all redirects history with objects
   
  # Example
  ``` python
  from sRequest import Elcap
  
  r = Elcap().get('http://python.org')
  
  print(r.text) # returned html code
  print(r.redirects) # returned 2 (redirects count)
  print(r.history[0].status_code) # HTTP/1.1 301 Moved Permanently
  print(r.status_code) # HTTP/1.1 200 OK
  print(r.url) # https://www.python.org/
```
