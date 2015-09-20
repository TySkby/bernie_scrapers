FROM python:2.7

RUN pip install -r requirements.txt

COPY ./scraper_scheduler.py /bin/scraper_scheduler.py

CMD ["/bin/scraper_scheduler.py"]
