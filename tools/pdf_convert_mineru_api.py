#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PRECISION_BASE_URL = "https://mineru.net/api/v4"
DEFAULT_TOKEN_ENV = "MINERU_API_TOKEN"
DEFAULT_OUTPUT_SUFFIX = ".mineru_api.md"
USER_AGENT = "llm_physics_wiki_mineru_api/1.0"
SHARED_TRIAL_TOKEN_PARTS = (
    "sk-Fv2y1I7Uahb9FFij",
    "0PDHfh65SKzifVVdPlUS",
    "KSXmB1cGKAJq",
)
SHARED_TRIAL_NOTICE = (
    "A shared trial token is provided for evaluation only. It may be unavailable or "
    "rate-limited. Create and configure your own free MinerU token for continued use."
)


class MinerUError(RuntimeError):
    pass


@dataclass
class HttpResponse:
    method: str
    url: str
    status_code: int
    body: bytes


@dataclass(frozen=True)
class TokenSelection:
    token: str
    is_shared_trial: bool


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a local PDF or remote URL through the MinerU precision API "
            "and save the returned Markdown locally."
        )
    )
    parser.add_argument(
        "input",
        help="Local file path or remote URL to parse.",
    )
    parser.add_argument(
        "--mode",
        choices=["precision"],
        default="precision",
        help="Compatibility option. Only the token-backed precision API is supported.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "Path to the Markdown output. Defaults to <input stem>.mineru_api.md for "
            "local files or <remote file stem>.mineru_api.md for URLs."
        ),
    )
    parser.add_argument(
        "--assets-dir",
        help=(
            "Directory for extracted result assets. For precision mode this stores the "
            "downloaded zip contents except the main Markdown file."
        ),
    )
    parser.add_argument(
        "--keep-zip",
        action="store_true",
        help="Keep the downloaded precision-API result zip next to the Markdown output.",
    )
    parser.add_argument(
        "--zip-output",
        help="Custom path for the downloaded precision-API result zip.",
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help=(
            "Environment variable that stores a personal precision API token. "
            f"Default: {DEFAULT_TOKEN_ENV}. If no personal token is set, the included "
            "shared trial token is used."
        ),
    )
    parser.add_argument(
        "--model-version",
        choices=["pipeline", "vlm", "MinerU-HTML"],
        default="vlm",
        help="Precision API model version. Default: vlm.",
    )
    parser.add_argument(
        "--language",
        default="en",
        help=(
            "Language hint sent to MinerU. Default: en, which matches the lecture-note "
            "PDFs in this vault better than the API default."
        ),
    )
    parser.add_argument(
        "--page-range",
        help=(
            "Optional page selector. Forwarded to the precision API as `page_ranges`."
        ),
    )
    parser.add_argument(
        "--data-id",
        help="Optional MinerU data_id for the request.",
    )
    parser.add_argument(
        "--extra-format",
        choices=["docx", "html", "latex"],
        action="append",
        default=[],
        help="Extra precision-API export formats to request in addition to Markdown/JSON.",
    )
    parser.add_argument(
        "--upload-backend",
        choices=["auto", "curl", "python"],
        default="auto",
        help=(
            "Signed upload implementation for local files. Default: auto "
            "(curl first, then Python fallback)."
        ),
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help=(
            "Enable OCR. Default is off; use it for exam papers, problem sheets, "
            "and other question sources when the precision API route is chosen."
        ),
    )
    parser.add_argument(
        "--disable-formula",
        action="store_true",
        help="Disable formula recognition.",
    )
    parser.add_argument(
        "--disable-table",
        action="store_true",
        help="Disable table recognition.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="HTTP request timeout in seconds. Default: 900.",
    )
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=3.0,
        help="Seconds between polling attempts. Default: 3.0.",
    )
    parser.add_argument(
        "--poll-timeout",
        type=int,
        default=1800,
        help="Maximum seconds to wait for MinerU to finish. Default: 1800.",
    )
    return parser


def is_remote_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def build_output_path(input_value: str, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()

    if is_remote_url(input_value):
        parsed = urlparse(input_value)
        name = Path(parsed.path).name or "mineru_api_output"
        stem = Path(name).stem or "mineru_api_output"
        return Path.cwd() / f"{stem}{DEFAULT_OUTPUT_SUFFIX}"

    input_path = Path(input_value).expanduser().resolve()
    return input_path.with_suffix(DEFAULT_OUTPUT_SUFFIX)


def build_asset_dir(output_path: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    base = output_path.with_suffix("")
    return base.parent / f"{base.name}_assets"


def build_zip_output_path(output_path: Path, explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    base = output_path.with_suffix("")
    return base.parent / f"{base.name}.zip"


def require_local_file(input_value: str) -> Path:
    path = Path(input_value).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input file not found: {path}")
    if not path.is_file():
        raise SystemExit(f"Input path is not a file: {path}")
    return path


def load_precision_token(env_name: str) -> TokenSelection:
    shared_trial_token = "".join(SHARED_TRIAL_TOKEN_PARTS)
    env_names = [env_name]
    if DEFAULT_TOKEN_ENV not in env_names:
        env_names.append(DEFAULT_TOKEN_ENV)

    shared_environment_token = ""
    for candidate in env_names:
        token = os.environ.get(candidate, "").strip()
        if token and token != shared_trial_token:
            return TokenSelection(
                token=token,
                is_shared_trial=False,
            )
        if token:
            shared_environment_token = token

    if shared_environment_token:
        return TokenSelection(
            token=shared_environment_token,
            is_shared_trial=True,
        )

    return TokenSelection(
        token=shared_trial_token,
        is_shared_trial=True,
    )


def build_precision_payload(args: argparse.Namespace, *, include_page_range: bool = True) -> dict[str, object]:
    payload: dict[str, object] = {
        "model_version": args.model_version,
        "enable_formula": not args.disable_formula,
        "enable_table": not args.disable_table,
        "is_ocr": args.ocr,
    }
    if args.language:
        payload["language"] = args.language
    if include_page_range and args.page_range:
        payload["page_ranges"] = args.page_range
    if args.extra_format:
        payload["extra_formats"] = args.extra_format
    return payload


def parse_json_response(response: HttpResponse) -> dict[str, object]:
    try:
        data = json.loads(response.body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise MinerUError(
            f"Expected JSON from {response.method} {response.url}, got invalid JSON"
        ) from exc
    if response.status_code >= 400:
        raise MinerUError(
            f"{response.method} {response.url} failed with HTTP {response.status_code}: {data}"
        )
    return data


def ensure_api_ok(payload: dict[str, object], context: str) -> dict[str, object]:
    code = payload.get("code")
    if code != 0:
        raise MinerUError(f"{context} failed with code={code}, msg={payload.get('msg')}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise MinerUError(f"{context} returned unexpected payload: {payload}")
    return data


def precision_headers(token: str) -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def http_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    json_body: dict[str, object] | None = None,
    data: bytes | None = None,
    timeout: int = 900,
) -> HttpResponse:
    method = method.upper()
    request_headers = dict(headers or {})
    payload = data
    if json_body is not None:
        payload = json.dumps(json_body).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")

    request = Request(url=url, data=payload, headers=request_headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return HttpResponse(
                method=method,
                url=response.geturl(),
                status_code=response.getcode(),
                body=body,
            )
    except HTTPError as exc:
        body = exc.read()
        return HttpResponse(
            method=method,
            url=exc.geturl(),
            status_code=exc.code,
            body=body,
        )
    except URLError as exc:
        raise MinerUError(f"{method} {url} failed: {exc}") from exc


def upload_file(url: str, file_path: Path, timeout: int, backend: str = "auto") -> None:
    curl_path = shutil.which("curl")
    curl_error = ""
    if backend in {"auto", "curl"} and curl_path:
        try:
            completed = subprocess.run(
                [
                    curl_path,
                    "--ipv4",
                    "--fail",
                    "--silent",
                    "--show-error",
                    "--connect-timeout",
                    "30",
                    "--max-time",
                    str(timeout),
                    "--request",
                    "PUT",
                    "--upload-file",
                    str(file_path),
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=timeout + 5,
            )
        except subprocess.TimeoutExpired as exc:
            curl_error = f"curl timed out after {timeout} seconds"
            if backend == "curl":
                raise MinerUError(f"Uploading {file_path.name} to MinerU failed: {curl_error}") from exc
        else:
            if completed.returncode == 0:
                return
            curl_error = completed.stderr.strip() or completed.stdout.strip() or "unknown curl error"
            if backend == "curl":
                raise MinerUError(f"Uploading {file_path.name} to MinerU failed: {curl_error}")
    elif backend == "curl":
        raise MinerUError("curl upload backend requested, but curl is not available")

    with file_path.open("rb") as handle:
        put_response = http_request(
            url,
            method="PUT",
            headers={"User-Agent": USER_AGENT},
            data=handle.read(),
            timeout=timeout,
        )
    if put_response.status_code not in {200, 201}:
        detail = ""
        if curl_error:
            detail = f"; curl fallback reason: {curl_error}"
        raise MinerUError(
            f"Uploading {file_path.name} to MinerU failed with HTTP {put_response.status_code}{detail}"
        )


def curl_download_to_bytes(url: str, timeout: int) -> bytes | None:
    curl_path = shutil.which("curl")
    if not curl_path:
        return None

    temp_dir = Path.cwd() / ".tmp_mineru_api"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"download-{int(time.time() * 1000)}.bin"
    try:
        completed = subprocess.run(
            [
                curl_path,
                "--ipv4",
                "--fail",
                "--silent",
                "--show-error",
                "--connect-timeout",
                "30",
                "--max-time",
                str(timeout),
                "--location",
                "--output",
                str(temp_path),
                url,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if completed.returncode != 0:
            return None
        return temp_path.read_bytes()
    finally:
        if temp_path.exists():
            temp_path.unlink()


def submit_precision_url(
    token: str,
    url: str,
    args: argparse.Namespace,
) -> str:
    payload = build_precision_payload(args)
    payload["url"] = url
    if args.data_id:
        payload["data_id"] = args.data_id
    response = http_request(
        f"{PRECISION_BASE_URL}/extract/task",
        method="POST",
        headers=precision_headers(token),
        json_body=payload,
        timeout=args.timeout,
    )
    data = ensure_api_ok(parse_json_response(response), "submit precision URL task")
    task_id = data.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise MinerUError(f"Precision URL submission did not return a task_id: {data}")
    return task_id


def submit_precision_local_file(
    token: str,
    file_path: Path,
    args: argparse.Namespace,
) -> str:
    payload = build_precision_payload(args, include_page_range=False)
    file_record: dict[str, object] = {"name": file_path.name}
    if args.data_id:
        file_record["data_id"] = args.data_id
    if args.page_range:
        file_record["page_ranges"] = args.page_range
    payload["files"] = [file_record]

    response = http_request(
        f"{PRECISION_BASE_URL}/file-urls/batch",
        method="POST",
        headers=precision_headers(token),
        json_body=payload,
        timeout=args.timeout,
    )
    data = ensure_api_ok(parse_json_response(response), "request precision upload URL")

    batch_id = data.get("batch_id")
    file_urls = data.get("file_urls")
    if not isinstance(batch_id, str) or not batch_id:
        raise MinerUError(f"Precision upload URL response missing batch_id: {data}")
    if not isinstance(file_urls, list) or len(file_urls) != 1 or not isinstance(file_urls[0], str):
        raise MinerUError(f"Precision upload URL response missing file_urls: {data}")

    upload_file(file_urls[0], file_path, args.timeout, args.upload_backend)

    return batch_id


def poll_precision_task(
    token: str,
    task_id: str,
    args: argparse.Namespace,
) -> str:
    start = time.time()
    last_state = None
    while time.time() - start < args.poll_timeout:
        response = http_request(
            f"{PRECISION_BASE_URL}/extract/task/{task_id}",
            headers=precision_headers(token),
            timeout=args.timeout,
        )
        data = ensure_api_ok(parse_json_response(response), "poll precision task")
        state = data.get("state")
        if state != last_state:
            print(f"Precision task {task_id}: state={state}")
            last_state = state
        if state == "done":
            full_zip_url = data.get("full_zip_url")
            if not isinstance(full_zip_url, str) or not full_zip_url:
                raise MinerUError(f"Precision task finished without full_zip_url: {data}")
            return full_zip_url
        if state == "failed":
            raise MinerUError(
                f"Precision task {task_id} failed: {data.get('err_msg') or 'unknown error'}"
            )
        time.sleep(args.poll_interval)
    raise MinerUError(
        f"Precision task {task_id} did not finish within {args.poll_timeout} seconds"
    )


def poll_precision_batch(
    token: str,
    batch_id: str,
    args: argparse.Namespace,
) -> str:
    start = time.time()
    last_state = None
    while time.time() - start < args.poll_timeout:
        response = http_request(
            f"{PRECISION_BASE_URL}/extract-results/batch/{batch_id}",
            headers=precision_headers(token),
            timeout=args.timeout,
        )
        data = ensure_api_ok(parse_json_response(response), "poll precision batch")
        results = data.get("extract_result")
        if not isinstance(results, list) or len(results) != 1 or not isinstance(results[0], dict):
            raise MinerUError(f"Precision batch returned unexpected extract_result: {data}")
        item = results[0]
        state = item.get("state")
        if state != last_state:
            print(f"Precision batch {batch_id}: state={state}")
            last_state = state
        if state == "done":
            full_zip_url = item.get("full_zip_url")
            if not isinstance(full_zip_url, str) or not full_zip_url:
                raise MinerUError(f"Precision batch finished without full_zip_url: {item}")
            return full_zip_url
        if state == "failed":
            raise MinerUError(
                f"Precision batch {batch_id} failed: {item.get('err_msg') or 'unknown error'}"
            )
        time.sleep(args.poll_interval)
    raise MinerUError(
        f"Precision batch {batch_id} did not finish within {args.poll_timeout} seconds"
    )


def download_bytes(url: str, timeout: int) -> bytes:
    curl_bytes = curl_download_to_bytes(url, timeout)
    if curl_bytes is not None:
        return curl_bytes
    response = http_request(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    if response.status_code >= 400:
        raise MinerUError(f"Downloading {url} failed with HTTP {response.status_code}")
    return response.body


def pick_markdown_member(archive: zipfile.ZipFile) -> str:
    names = archive.namelist()
    if "full.md" in names:
        return "full.md"
    md_names = [name for name in names if name.lower().endswith(".md")]
    if len(md_names) == 1:
        return md_names[0]
    raise MinerUError(
        f"Could not uniquely identify the main Markdown file in MinerU zip: {md_names}"
    )


def should_prefix_target(target: str, asset_roots: set[str]) -> bool:
    if not target or target.startswith(("#", "/", "http://", "https://", "mailto:", "data:")):
        return False
    clean = target.lstrip("./")
    if not clean:
        return False
    root = clean.split("/", 1)[0]
    return root in asset_roots


def rewrite_markdown_targets(markdown: str, asset_dir_name: str, asset_roots: set[str]) -> str:
    if not asset_roots:
        return markdown

    def replace_link(match: re.Match[str]) -> str:
        left, target, right = match.groups()
        if should_prefix_target(target, asset_roots):
            target = f"{asset_dir_name}/{target.lstrip('./')}"
        return f"({left}{target}{right})"

    def replace_attr(match: re.Match[str]) -> str:
        prefix, quote, target = match.groups()
        if should_prefix_target(target, asset_roots):
            target = f"{asset_dir_name}/{target.lstrip('./')}"
        return f"{prefix}={quote}{target}{quote}"

    markdown = re.sub(r"\((<?)([^)\s>]+)(>?)\)", replace_link, markdown)
    markdown = re.sub(r"\b(src|href)=(['\"])([^'\"]+)\2", replace_attr, markdown)
    return markdown


def write_precision_markdown_bundle(
    zip_bytes: bytes,
    output_path: Path,
    asset_dir: Path,
    keep_zip: bool,
    zip_output_path: Path,
) -> None:
    if asset_dir.exists():
        shutil.rmtree(asset_dir)
    asset_dir.mkdir(parents=True, exist_ok=True)

    if keep_zip:
        zip_output_path.parent.mkdir(parents=True, exist_ok=True)
        zip_output_path.write_bytes(zip_bytes)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        markdown_member = pick_markdown_member(archive)
        markdown = archive.read(markdown_member).decode("utf-8")

        asset_roots: set[str] = set()
        for member in archive.infolist():
            if member.is_dir() or member.filename == markdown_member:
                continue
            target = asset_dir / member.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(member))
            asset_roots.add(member.filename.split("/", 1)[0])

    rewritten = rewrite_markdown_targets(markdown, asset_dir.name, asset_roots)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rewritten, encoding="utf-8")


def main() -> int:
    args = make_parser().parse_args()
    output_path = build_output_path(args.input, args.output)
    asset_dir = build_asset_dir(output_path, args.assets_dir)
    zip_output_path = build_zip_output_path(output_path, args.zip_output)

    try:
        token_selection = load_precision_token(args.token_env)
        token = token_selection.token
        if is_remote_url(args.input):
            task_id = submit_precision_url(token, args.input, args)
            print(f"Submitted precision URL task: {task_id}")
            result_zip_url = poll_precision_task(token, task_id, args)
        else:
            file_path = require_local_file(args.input)
            batch_id = submit_precision_local_file(token, file_path, args)
            print(f"Uploaded local file to precision API batch: {batch_id}")
            result_zip_url = poll_precision_batch(token, batch_id, args)

        print(f"Downloading precision result zip: {result_zip_url}")
        zip_bytes = download_bytes(result_zip_url, args.timeout)
        write_precision_markdown_bundle(
            zip_bytes=zip_bytes,
            output_path=output_path,
            asset_dir=asset_dir,
            keep_zip=args.keep_zip,
            zip_output_path=zip_output_path,
        )
        print(f"Wrote {output_path}")
        print(f"Extracted precision assets to {asset_dir}")
        if args.keep_zip:
            print(f"Saved result zip to {zip_output_path}")
        if token_selection.is_shared_trial:
            print(SHARED_TRIAL_NOTICE)
        return 0
    except MinerUError as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    raise SystemExit(main())

