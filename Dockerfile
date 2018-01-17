FROM python:2.7.14-alpine3.7

ADD redirect.py /
ADD templates/ /templates/
ADD guni.conf /

RUN pip install flask
RUN pip install gunicorn
RUN pip install configparser

EXPOSE 5000

CMD ["gunicorn","-c", "/guni.conf", "redirect:app"]

