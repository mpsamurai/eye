FROM mpsamurai/neochi-dev-base:20190424-raspbian

COPY ./requirements.txt /tmp
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /code
COPY ./src /code

#CMD ["python", "eye.py"]
