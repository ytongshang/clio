import asyncio
import hashlib
import os
import shutil
from typing import Any, Callable, Dict, Literal, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import aiohttp

from clio.utils import Log


class HttpException(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause

    def __str__(self):
        if self.cause is None:
            return super().__str__()
        return f"{super().__str__()}, caused by {self.cause}"


class RawResponse:
    def __init__(self, headers, body, status_code=-1):
        self.headers = headers
        self.body = body
        self.status_code = status_code


def default_valid_status(status_code: int) -> bool:
    return 200 == status_code


# noinspection DuplicatedCode,PyShadowingNames
async def http_invoke(
    url: str,
    method: Literal["GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS"] = "GET",
    query: Optional[dict[str, Any]] = None,
    json: Any = None,
    data: Any = None,
    response_type: Literal["json", "text", "bytes"] = "json",
    headers: Optional[dict[str, str]] = None,
    timeout: int = 30,
    verbose: bool = True,
    validate_status: Optional[Callable[[int], bool]] = default_valid_status,
    proxy: str = "",
) -> RawResponse:
    try:
        async with aiohttp.ClientSession() as session:
            request_url_str = url_append_query(url, query)

            if verbose:
                request_log = [f"方法: {method}", f"URL: {request_url_str}"]
                if data is not None:
                    request_log.append(f"data: {data}")
                if json is not None:
                    request_log.append(f"json: {json}")
                if headers is not None:
                    request_log.append(f"请求头: {headers}")
                Log.debug(f"http 调用, {', '.join(request_log)}")

            if data is not None and json is not None:
                raise ValueError(
                    "data and json parameters can not be used at the same time"
                )

            try:
                async with session.request(
                    method,
                    request_url_str,
                    json=json,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    proxy=proxy,
                ) as response:
                    response_headers = response.headers

                    valid_status = validate_status or default_valid_status
                    if not valid_status(response.status):
                        raise HttpException(f"响应状态码为 {response.status}")

                    if response_type == "json":
                        resp = await response.json()
                    elif response_type == "text":
                        resp = await response.text()
                    elif response_type == "bytes":
                        resp = await response.read()
                    else:
                        raise HttpException(f"不支持的响应类型{response_type}")

                    if verbose:
                        Log.debug(f"resp: {resp}")
                    return RawResponse(response_headers, resp, response.status)
            except Exception as e:
                raise HttpException(f"请求 URL[{url}] 错误", e)
    except Exception as e:
        if verbose:
            Log.error(f"http 调用 {request_url_str} 失败, {e}")
        raise e


async def download_file(
    url: str, save_path, delete_if_exists: bool = False, verbose: bool = True
):
    if not url:
        raise HttpException("download url is empty")

    if not save_path:
        raise HttpException("save path is empty")

    exists = os.path.exists(save_path)
    is_file = os.path.isfile(save_path)
    if not delete_if_exists and exists and is_file:
        if verbose:
            Log.info(f"download url[{url}] to path[{save_path}], file exists, skip")
        return

    if exists:
        try:
            if is_file:
                os.remove(save_path)
            else:
                shutil.rmtree(save_path)
        except Exception as e:
            raise HttpException(f"delete file[{save_path}] error", e)

    await asyncio.sleep(1)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(save_path, "wb") as fd:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        fd.write(chunk)
                    fd.flush()
    except Exception as e:
        raise HttpException(f"download url[{url}] to path[{save_path}] error", e)


# noinspection PyShadowingNames
def url_append_query(url: str, query: Optional[Dict[str, Any]]) -> str:
    request_url_str = url
    try:
        url_parts = urlparse(url)
    except Exception as e:
        raise HttpException(f"parse url[{url}] error", e)

    if query is not None:
        try:
            original_query = parse_qs(url_parts.query)
            original_query.update(query)
            encoded_query = urlencode(original_query, doseq=True)
            new_url_parts = url_parts._replace(query=encoded_query)
            new_url = urlunparse(new_url_parts)
            request_url_str = str(new_url)
        except Exception as e:
            raise HttpException(f"parse query[{query}] error", e)
    return request_url_str


def file_name_generator(file_name: str):
    suffix_index = file_name.rindex(".")
    file_name_prefix = file_name[:suffix_index]
    suffix = file_name[suffix_index + 1 :]
    # md5
    md5_hash = hashlib.md5()
    md5_hash.update(file_name_prefix.encode())
    digest = md5_hash.hexdigest()
    return f"{digest}.{suffix}"
