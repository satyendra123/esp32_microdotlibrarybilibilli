#step-1 urequest.py

import usocket

ITER_CHUNK_SIZE = 128


class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._content_consumed = False
        self._cached = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __iter__(self):
        return self.iter_content()

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson

        return ujson.loads(self.content)

    def iter_content(self, chunk_size=ITER_CHUNK_SIZE):
        def generate():
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk
            self._content_consumed = True

        if self._content_consumed:
            raise RuntimeError("response already consumed")
        elif chunk_size is not None and not isinstance(chunk_size, int):
            raise TypeError(
                "chunk_size must be an int, it is instead a %s."
                % type(chunk_size)
            )

        return generate()

    def iter_lines(self, chunk_size=ITER_CHUNK_SIZE, delimiter=None):
        pending = None

        for chunk in self.iter_content(chunk_size=chunk_size):

            if pending is not None:
                chunk = pending + chunk

            if delimiter:
                lines = chunk.split(delimiter)
            else:
                lines = chunk.split(b"\n")

            if lines and lines[-1] and chunk and lines[-1][-1] == chunk[-1]:
                pending = lines.pop()
            else:
                pending = None

            for line in lines:
                yield line

        if pending is not None:
            yield pending


def request(
    method,
    url,
    data=None,
    json=None,
    headers={},
    stream=None,
    timeout=None,
    parse_headers=True,
):

    redirect = None

    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import tls

        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    resp_d = None
    if parse_headers is not False:
        resp_d = {}

    s = usocket.socket(ai[0], ai[1], ai[2])

    if timeout is not None:
        # Note: settimeout is not supported on all platforms, will raise
        # an AttributeError if not available.
        s.settimeout(timeout)

    try:
        s.connect(ai[-1])
        if proto == "https:":
            context = tls.SSLContext(tls.PROTOCOL_TLS_CLIENT)
            context.verify_mode = tls.CERT_NONE
            s = context.wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
        if "Host" not in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")
        if json is not None:
            assert data is None
            import ujson

            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
        if data:
            s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"\r\n")
        if data:
            s.write(data)

        line = s.readline()
        # print(l)
        line = line.split(None, 2)
        status = int(line[1])
        reason = ""
        if len(line) > 2:
            reason = line[2].rstrip()
        while True:
            line = s.readline()
            if not line or line == b"\r\n":
                break
            # print(l)
            if line.startswith(b"Transfer-Encoding:"):
                if b"chunked" in line:
                    raise ValueError("Unsupported " + str(line, "utf-8"))
            elif line.startswith(b"Location:") and not 200 <= status <= 299:
                if status in [301, 302, 303, 307, 308]:
                    redirect = str(line[10:-2], "utf-8")
                else:
                    raise NotImplementedError(
                        "Redirect %d not yet supported" % status
                    )
    except OSError:
        s.close()
        raise

    if redirect:
        s.close()
        if status in [301, 302, 303]:
            return request("GET", redirect, None, None, headers, stream)
        else:
            return request(method, redirect, data, json, headers, stream)
    else:
        resp = Response(s)
        resp.status_code = status
        resp.reason = reason
        if resp_d is not None:
            resp.headers = resp_d
        return resp


def head(url, **kw):
    return request("HEAD", url, **kw)


def get(url, **kw):
    return request("GET", url, **kw)


def post(url, **kw):
    return request("POST", url, **kw)


def put(url, **kw):
    return request("PUT", url, **kw)


def patch(url, **kw):
    return request("PATCH", url, **kw)


def delete(url, **kw):
    return request("DELETE", url, **kw)
