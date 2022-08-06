FROM python:latest AS builder
RUN mkdir -p /src/
COPY ./ /src/
RUN mkdir -p /dist
WORKDIR /src
RUN python3 -m pip install build
RUN python3 -m build --wheel --outdir /dist
RUN ls -lR /dist

FROM python:latest
COPY --from=builder /dist/scadgen-0.0.1-py3-none-any.whl /tmp/scadgen-0.0.1-py3-none-any.whl
RUN python3 -m pip install /tmp/scadgen-0.0.1-py3-none-any.whl
RUN rm -f /tmp/scadgen-0.0.1-py3-none-any.whl
RUN python3 -m unittest scadgen.scadobj_test
