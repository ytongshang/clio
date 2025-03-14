import asyncio
import hashlib
import os
import shutil
from typing import Any, Callable, Dict, Literal, Optional, Union
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import aiofiles
import httpx
from httpx import URL, Proxy

from clio.utils import Log

ProxiesTypes = Union[URL, str, Proxy]


class HttpException(Exception):
    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        status_code: Optional[int] = None,
        body: Optional[str] = None,
    ):
        super().__init__(message)
        self.cause = cause
        self.status_code = status_code
        self.body = body

    def __str__(self):
        if self.cause is None:
            return super().__str__()
        return f"{super().__str__()}, caused by {self.cause}"


class RawResponse:
    def __init__(self, headers, body, status_code=-1):
        self.headers = headers
        self.body = body
        self.status_code = status_code


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
    suffix_index = file_name.rfind(".")
    if suffix_index != -1:
        file_name_prefix = file_name[:suffix_index]
        suffix = file_name[suffix_index + 1 :]
        md5_hash = hashlib.md5()
        md5_hash.update(file_name_prefix.encode())
        digest = md5_hash.hexdigest()
        return f"{digest}.{suffix}"
    else:
        md5_hash = hashlib.md5()
        md5_hash.update(file_name.encode())
        digest = md5_hash.hexdigest()
        return digest


def default_valid_status(status_code: int) -> bool:
    return 200 == status_code


async def http_invoke(
    url: str,
    method: Literal["GET", "POST", "DELETE", "PUT", "HEAD", "OPTIONS"] = "GET",
    query: Optional[dict[str, Any]] = None,
    json: Any = None,
    data: Any = None,
    response_type: Literal["json", "text"] = "json",
    headers: Optional[dict[str, str]] = None,
    timeout: int = 30,
    verbose: bool = True,
    validate_status: Optional[Callable[[int], bool]] = default_valid_status,
    proxies: Optional[ProxiesTypes] = None,
) -> RawResponse:
    try:
        async with httpx.AsyncClient(proxy=proxies) as client:
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
                raise HttpException(
                    "data and json parameters can not be used at the same time"
                )

            response = await client.request(
                method,
                request_url_str,
                json=json,
                data=data,
                headers=headers,
                timeout=timeout,
            )

            response_headers = response.headers

            valid_status = validate_status or default_valid_status
            if not valid_status(response.status_code):
                raise HttpException(
                    message=f"响应状态码为 {response.status_code}",
                    status_code=response.status_code,
                    body=response.text,
                )
            if response_type == "json":
                resp = response.json()
            elif response_type == "text":
                resp = response.text
            else:
                raise HttpException(f"不支持的响应类型{response_type}")
            if verbose:
                Log.debug(f"resp: {resp}")
            return RawResponse(response_headers, resp, response.status_code)
    except Exception as e:
        if isinstance(e, HttpException):
            raise
        else:
            raise HttpException(f"http 调用 {request_url_str} 失败", cause=e)


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
    temp_file_path = f"{save_path}.temp"

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream("GET", url) as response:
                if response.status_code != 200:
                    raise HttpException(
                        f"download url[{url}] error, status[{response.status_code}]"
                    )
                async with aiofiles.open(temp_file_path, "wb") as fd:
                    async for chunk in response.aiter_bytes(4096):
                        await fd.write(chunk)
                    await fd.flush()
        except Exception as e:
            if isinstance(e, HttpException):
                raise e
            else:
                raise HttpException(
                    f"download url[{url}] to path[{save_path}] error", e
                )

    # rename temp file to save path
    try:
        os.rename(temp_file_path, save_path)
    except Exception as e:
        try:
            os.remove(temp_file_path)
        except:
            pass
        raise HttpException(
            f"rename temp file[{temp_file_path}] to save path[{save_path}] error", e
        )
