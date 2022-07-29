FROM python:3.9

#
WORKDIR /code

#
COPY ./downloader-requirnment.txt /code/downloader-requirnment.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/downloader-requirnment.txt

#
COPY ./app /code/app

#
ENTRYPOINT ["python","app/downloader-utility.py" ]
