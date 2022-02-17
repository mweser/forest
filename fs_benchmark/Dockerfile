FROM ubuntu:hirsute as libbuilder
WORKDIR /app
RUN ln --symbolic --force --no-dereference /usr/share/zoneinfo/EST && echo "EST" > /etc/timezone
RUN apt update && DEBIAN_FRONTEND="noninteractive" apt upgrade -y
RUN apt update -y && DEBIAN_FRONTEND="noninteractive" apt install -yy python3.9 python3.9-venv pipenv
RUN python3.9 -m venv /app/venv
COPY Pipfile.lock Pipfile /app/
RUN VIRTUAL_ENV=/app/venv pipenv install

FROM ubuntu:hirsute
WORKDIR /app
RUN apt update && apt install -y python3.9 wget kmod
RUN apt-get clean autoclean && apt-get autoremove --yes && rm -rf /var/lib/{apt,dpkg,cache,log}/

COPY --from=libbuilder /app/venv/lib/python3.9/site-packages /app/
COPY ./mc_util/ /app/mc_util/
COPY ./mypy.ini ./*.py /app/
RUN ["pytest"]
