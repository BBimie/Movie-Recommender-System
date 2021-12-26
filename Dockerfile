# # pulling the python image
# FROM python:3.9-alpine

# # copy the requirements file into the image
# COPY ./requirements.txt /app/requirements.txt

# # switch working directory
# WORKDIR /app

# # install the dependencies and packages in the requirements file
# RUN pip install -r requirements.txt

# # copy every content from the local file to the image
# COPY . /app

# # configure the container to run in an executed manner
# ENTRYPOINT [ "python" ]

# CMD ["app.py"]

FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip
RUN pip install certifi==2021.10.8
RUN pip install charset-normalizer==2.0.9
RUN pip install click==8.0.3
RUN pip install Flask==2.0.2
RUN pip install gunicorn==20.1.0
RUN pip install idna==3.3
RUN pip install itsdangerous==2.0.1
RUN pip install Jinja2==3.0.3
RUN pip install joblib==1.1.0
RUN pip install MarkupSafe==2.0.1
RUN pip install numpy
RUN pip install pandas==1.3.0
RUN pip install python-dateutil==2.8.2
RUN pip install pytz==2021.3
RUN pip install regex==2021.11.10
RUN pip install requests==2.26.0
RUN pip install scikit-learn==1.0.2
RUN pip install scipy==1.7.3
RUN pip install six==1.16.0
RUN pip install sklearn==0.0
RUN pip install tmdbsimple==2.8.1
RUN pip install tqdm==4.62.3
RUN pip install urllib3==1.26.7
RUN pip install Werkzeug==2.0.2

#RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
