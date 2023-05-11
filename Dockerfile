FROM python:3.9

#
WORKDIR /code

#
COPY ./requirnment.txt /code/requirnment.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirnment.txt

#
COPY ./app /code/app

#
ENTRYPOINT ["python","app/downloader-utility.py" ]
