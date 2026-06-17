FROM python:3.12

#
WORKDIR /code

#
COPY ./requirement.txt /code/requirement.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirement.txt

#
COPY ./app /code/app

# Run as an unprivileged user so a download bug cannot write as root.
RUN useradd --create-home --uid 10001 appuser && chown -R appuser /code
USER appuser

#
ENTRYPOINT ["python","app/downloader-utility.py" ]
