FROM python

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD [ "pytest", "--html=report.html", "--self-contained-html" ]