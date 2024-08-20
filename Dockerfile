FROM ubuntu:22.04
WORKDIR /app
RUN apt-get update && apt-get install -y python3.11 python3.11-dev && apt-get install -y python3-pip 
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY create_documents.py \
     vectorize.py \
     main.py\
     f1120.pdf\
     f1120sd.pdf \
     if1120.txt \
     if1120sd.txt \
     link_chunks.py \
     create_relationships.py \ 
    ./
#COPY main.py .
#COPY llama.py \
#     main.py\
#     test_request.py\
#     agents.py \
#     parse.py \ 
#     chain.py \
#    ./
#COPY dir1 dir2 ./
#CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

#docker run --mount type=bind,source=C:\Users\Adam.Conovaloff\langchain\vectorstore\bind,target=/app/persist -p 8000:8000  vectorstore:0
