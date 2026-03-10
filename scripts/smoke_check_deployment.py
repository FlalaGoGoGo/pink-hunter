#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import ssl
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(url: str, insecure: bool = False) -> tuple[int, bytes]:
    request = Request(url, headers={"User-Agent": "pink-hunter-smoke-check/1.0"})
    context = ssl._create_unverified_context() if insecure else None
    with urlopen(request, timeout=20, context=context) as response:
        return response.status, response.read()


def check_json(url: str, insecure: bool = False) -> dict[str, object]:
    status, payload = fetch(url, insecure=insecure)
    parsed = json.loads(payload.decode("utf-8"))
    return {"url": url, "status": status, "json_ok": isinstance(parsed, dict)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-check Pink Hunter deployment endpoints.")
    parser.add_argument("--site-url", required=True, help="Base site URL, e.g. https://next.pinkhunter.flalaz.com")
    parser.add_argument("--api-base-url", help="Visitor API base URL, e.g. https://abc.execute-api.us-west-2.amazonaws.com")
    parser.add_argument("--data-base-url", help="Data base URL; defaults to the site URL.")
    parser.add_argument("--insecure", action="store_true", help="Skip TLS certificate verification.")
    args = parser.parse_args()

    site_url = args.site_url.rstrip("/")
    data_base_url = (args.data_base_url or site_url).rstrip("/")
    results: list[dict[str, object]] = []

    try:
      site_status, _ = fetch(site_url, insecure=args.insecure)
      results.append({"url": site_url, "status": site_status, "json_ok": None})
      results.append(check_json(f"{data_base_url}/data/meta.v2.json", insecure=args.insecure))
      results.append(check_json(f"{data_base_url}/data/jump-index.v1.json", insecure=args.insecure))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
      print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
      return 1

    if args.api_base_url:
        api_base = args.api_base_url.rstrip("/")
        try:
            results.append(check_json(f"{api_base}/api/v1/visitor-count", insecure=args.insecure))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(json.dumps({"ok": False, "error": str(exc), "results": results}, ensure_ascii=False))
            return 1

    ok = all(int(item["status"]) == 200 for item in results)
    print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
