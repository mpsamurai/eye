FROM mpsamurai/neochi-dev-base:20190424-x64

COPY ./requirements.txt /tmp

WORKDIR /code
COPY ./src /code

#CMD ["python", "eye.py"]
