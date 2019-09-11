# redirect_resolver
Application for resolving of HTTP redirects

# Building
If you don't have python-3.6.9 on your machine or your setup is specific - you may use Docker for executing resolver and running the tests.

Just make sure that docker daemon is running and run `./build`

# Running

In docker:
```bash
#./run <url>
#example
> ./run http://www.ya.ru
https://ya.ru/
```

without docker:
```bash
> ./redirect_resolver.py http://www.ya.ru
https://ya.ru/
```

for getting the help:
```bash
> ./redirect_resolver.py --help
usage: redirect_resolver.py [-h] [--max-redirects MAX_REDIRECTS]
                            [--ignore-unlimited-content]
                            url

positional arguments:
  url                   URL for resolving

optional arguments:
  -h, --help            show this help message and exit
  --max-redirects MAX_REDIRECTS
                        Maximum number of redirects
  --ignore-unlimited-content
                        Don't rise an exception if content may have unlimited
                        size
```

# Testing

For running tests in docker just type: `./test`.

For running tests without docker you need to install `requirements-dev.txt` and type `./script/do_test`
