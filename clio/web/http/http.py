import asyncio
import logging
import os
import shutil
from typing import Any, Callable, Literal, Optional
from urllib.parse import urlencode, urlparse, urlunparse

import aiohttp

__logger__ = logging.getLogger()

from clio import Log


class HttpException(Exception):
    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause

    def __str__(self):
        if self.cause is None:
            return super().__str__()
        return f"{super().__str__()}, caused by {self.cause}"


class RawResponse:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body


def default_valid_status(status_code: int) -> bool:
    return 200 == status_code


async def http_invoke(
    url: str,
    method: Literal["GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS"] = "GET",
    headers: Optional[dict[str, str]] = None,
    query: Optional[dict[str, Any]] = None,
    json: Any = None,
    data: Any = None,
    files: Optional[dict[str, Any]] = None,
    response_type: Literal["json", "text", "bytes"] = "json",
    timeout: int = 10,
    proxy: str = "",
    validate_status: Optional[Callable[[int], bool]] = default_valid_status,
    verbose: bool = True,
) -> RawResponse:
    try:
        async with aiohttp.ClientSession() as session:
            request_url_str = url
            try:
                request_url = urlparse(url)
            except Exception as e:
                raise HttpException(f"url解析出错:{url}", e)

            if query is not None:
                try:
                    query_string = urlencode(query)
                    new_url_parts = request_url._replace(query=query_string)
                    request_url_str = str(urlunparse(new_url_parts))
                except Exception as e:
                    raise HttpException(f"query参数错误: {query}", e)

            if verbose:
                request_log = [f"方法: {method}", f"URL: {request_url_str}"]
                if data is not None:
                    request_log.append(f"data: {data}")
                if json is not None:
                    request_log.append(f"json: {json}")
                if files is not None and len(files) > 0:
                    request_log.append(f"文件: {files.keys()}")
                if headers is not None:
                    request_log.append(f"请求头: {headers}")
                __logger__.debug(f"http 调用, {', '.join(request_log)}")

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
                    status_code = response.status
                    valid_status = validate_status or default_valid_status
                    if not valid_status(status_code):
                        raise HttpException(f"响应状态码为 {response.status}")

                    if response_type == "json":
                        resp = await response.json()
                    elif response_type == "text":
                        resp = await response.text()
                    elif response_type == "bytes":
                        resp = await response.read()
                    else:
                        raise HttpException(f"不支持的响应类型{response_type}")
                    return RawResponse(response_headers, resp)

            except Exception as e:
                raise HttpException(f"请求 URL[{url}] 错误", e)
    except Exception as e:
        if verbose:
            __logger__.error(f"http 调用 {request_url_str} 失败, {e}")
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
