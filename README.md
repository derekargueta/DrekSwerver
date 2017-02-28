DrekSwerver
=============

A *very* tiny experimental event-driven web server.

This started out as a class project for [BYU CS 360: Internet Programming](http://cs360.byu.edu/fall-2015/labs/web-server) but I now use it for kicks and giggles to try out new things.

Features:
- `Range` header support
- `Etag` support

TODO:
- [ ] request proxying
- [ ] support `Last-Modified` and `If-Modified-Since`
- [ ] support basic compression algorithms and `Content-Encoding` header
- [ ] support `X-XSS-Protection`
- [ ] support `Keep-Alive`
- [ ] support `Cache-Control`
- [ ] support `Vary`
- [ ] support `Content-Language`

### Setup
Really the only requirement for this is [Vagrant](https://www.vagrantup.com/). `vagrant up` should handle all project setup which includes setting up a Linux box, installing Python 3, and installing dependencies.

