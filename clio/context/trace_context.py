import base64
import random
import struct
import time
from typing import Any, Dict

from .globals import has_request_context, request_context


class TraceContext:
    X_TRACE_ID = "x-trace-id"
    TRACE_EXTRA = "__trace_extra"

    def __init__(self, app_name: str):
        self.app_name = app_name

    def parse_trace_id(self, scope, context) -> Dict[str, str]:
        raw_headers = list(scope.get("headers", []))
        headers = {}
        for key, value in raw_headers:
            headers[key.decode("latin-1")] = value.decode("latin-1")
        trace_id = headers.get(TraceContext.X_TRACE_ID, "")
        if not trace_id:
            unique_id = self.create_unique_id()
            trace_id = f"{self.app_name}-{unique_id}"
        m = {TraceContext.X_TRACE_ID: trace_id}
        extra_m = context.get(TraceContext.TRACE_EXTRA, {})
        extra_m.update(m)
        context.set(TraceContext.TRACE_EXTRA, extra_m)
        return m

    def trace_id(self):
        extra_map = self.trace_extra()
        return extra_map.get(TraceContext.X_TRACE_ID, "")

    def trace_extra(self):
        if has_request_context():
            return request_context().get("__trace_extra", {})
        return {}

    def trace_extra_update(self, data: Dict[str, Any]):
        if has_request_context():
            ctx = request_context()
            trace_extra = ctx.get("__trace_extra", {})
            trace_extra.update(data)
            ctx.set("__trace_extra", trace_extra)

    def patch_http_invoke(self, headers: Dict[str, str]):
        trace_id = self.trace_id()
        if trace_id:
            headers.update({TraceContext.X_TRACE_ID: trace_id})

    def create_unique_id(
        self,
    ):
        time_ns = time.time_ns()
        return self.time_based_unique_id(time_ns, 0)

    def time_based_unique_id(self, timestamp, scale):
        timestamp_bigint = int(timestamp)
        random_long = self.next_long()
        scale_bigint = int(scale)
        if scale_bigint > 0:
            timestamp_bigint = timestamp_bigint * scale_bigint + (
                random_long % scale_bigint
            )
        buf = bytearray(16)
        struct.pack_into(">q", buf, 0, timestamp_bigint)
        struct.pack_into(">q", buf, 8, random_long)
        result = base64.b64encode(buf).decode("ascii")
        return result.replace("+", "-").replace("/", "_").rstrip("=")

    def next_long(self):
        return random.randint(-9223372036854775808, 9223372036854775807)
