FROM ubuntu:22.04
WORKDIR /app
RUN apt-get update && apt-get install -y python3.11 python3.11-dev && apt-get install -y python3-pip 
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY create_documents.py \
     vectorize.py \
     main.py\
     irs_documents\
     link_chunks.py \
     create_relationships.py \ 
    ./

#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

