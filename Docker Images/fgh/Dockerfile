# Linux Debian Image
FROM debian:buster


# Installing basic support libraries.
RUN apt-get update \
    && apt-get install -y \
        curl \
        libxrender1 \
        libjpeg62-turbo \
        fontconfig \
        libxtst6 \
        xfonts-75dpi \
        xfonts-base \
        xz-utils


# Fetching wkhtmltopdf software (coverts html to pdf)
RUN curl "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb" -L -o "wkhtmltopdf.deb"
RUN dpkg -i wkhtmltopdf.deb


# Installing Python & pip
RUN apt install -y python3 python3-pip python3-dev python-pip python-dev


# Installing required python libraries for stage 3.
RUN pip3 install pypdf2 py3-wkhtmltopdf pdfkit pathlib
RUN pip install pathlib

