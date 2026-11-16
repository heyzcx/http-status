#!/usr/bin/env python3
"""Check HTTP status codes and response times for one or more URLs.

Usage:
    python3 http_status.py https://example.com https://github.com
    python3 http_status.py -f urls.txt
    python3 http_status.py --timeout 5 --method HEAD https://example.com
    echo "https://example.com" | python3 http_status.py

Zero dependencies, standard library only.
"""

import argparse
import sys
import time
import urllib.error
import urllib.request


def check_url(url, timeout=10, method="GET"):
    """Return (status, elapsed_ms, error) for a single URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    req = urllib.request.Request(url, method=method)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # Read a small chunk so the timing includes body transfer start.
            resp.read(1024)
            return resp.status, (time.monotonic() - start) * 1000, None
    except urllib.error.HTTPError as e:
        return e.code, (time.monotonic() - start) * 1000, None
    except urllib.error.URLError as e:
        return None, (time.monotonic() - start) * 1000, str(e.reason)
    except (TimeoutError, OSError) as e:
        return None, (time.monotonic() - start) * 1000, str(e)


def status_label(status):
    if status is None:
        return "ERROR"
    if 200 <= status < 300:
        return "OK"
    if 300 <= status < 400:
        return "REDIRECT"
    if 400 <= status < 500:
        return "CLIENT ERROR"
    return "SERVER ERROR"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check HTTP status codes and response times for URLs."
    )
    parser.add_argument("urls", nargs="*", help="URLs to check")
    parser.add_argument("-f", "--file", help="file with one URL per line")
    parser.add_argument("--timeout", type=float, default=10,
                        help="request timeout in seconds (default: 10)")
    parser.add_argument("--method", default="GET", choices=["GET", "HEAD"],
                        help="HTTP method (default: GET)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="only print non-2xx results")
    args = parser.parse_args(argv)

    urls = list(args.urls)
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                urls.extend(line.strip() for line in f
                            if line.strip() and not line.startswith("#"))
        except OSError as e:
            print(f"error: cannot read {args.file}: {e}", file=sys.stderr)
            return 2
    if not sys.stdin.isatty():
        urls.extend(line.strip() for line in sys.stdin if line.strip())
    if not urls:
        parser.print_usage(sys.stderr)
        print("error: no URLs given", file=sys.stderr)
        return 2

    seen = set()
    worst = 0
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        status, elapsed, error = check_url(url, args.timeout, args.method)
        if status is None:
            worst = 2
            if not args.quiet:
                print(f"{'ERROR':>4}  {elapsed:7.0f} ms  {url}  ({error})")
            else:
                print(f"ERROR  {url}  ({error})")
            continue
        label = status_label(status)
        if status >= 400:
            worst = 2
        elif status >= 300 and worst < 1:
            worst = 1
        if args.quiet and status < 300:
            continue
        print(f"{status:>4}  {label:<13} {elapsed:7.0f} ms  {url}")

    return worst


if __name__ == "__main__":
    sys.exit(main())
