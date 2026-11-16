# http-status

Check HTTP status codes and response times for one or more URLs — zero-dependency Python CLI.

## Usage

```bash
python3 http_status.py https://example.com https://github.com
python3 http_status.py -f urls.txt
python3 http_status.py --timeout 5 --method HEAD https://example.com
echo "https://example.com" | python3 http_status.py
```

URLs can come from arguments, a file (`-f`, one URL per line, `#` comments
ignored), or stdin. A missing scheme defaults to `https://`.

## Options

| Option | Description |
| --- | --- |
| `-f, --file FILE` | Read URLs from a file, one per line |
| `--timeout SECONDS` | Request timeout (default: 10) |
| `--method GET\|HEAD` | HTTP method (default: GET) |
| `-q, --quiet` | Only print non-2xx results |

## Output

Each line shows the status code, a short label, the response time, and the URL:

```
 200  OK                 35 ms  https://example.com
 404  CLIENT ERROR        7 ms  https://example.com/nope
ERROR                    12 ms  https://down.example  ([Errno -2] Name or service not known)
```

## Exit codes

- `0` — every URL returned 2xx
- `1` — at least one URL returned 3xx
- `2` — at least one URL returned 4xx/5xx, failed to connect, or no URLs were given

## Requirements

Python 3.8+ with no third-party packages.
