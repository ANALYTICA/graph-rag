# graph-rag
Containerized example of an LLM using graphRAG on IRS documents with a 
chatbot front-end interface. 

Before running, in the top level of the repo, create the following folders 
to mount to the Neo4j database container:

```
mkdir plugins
mkdir import
mkdir data
```
You will also need an LLM. You can download a suitable model here:

https://huggingface.co/TheBloke/CapybaraHermes-2.5-Mistral-7B-GGUF/blob/main/capybarahermes-2.5-mistral-7b.Q5_K_M.gguf

It is around 5 GB. Feel free to download more up-to-date models. However,
they must be llama-cpp compliant. 

The model must be placed in the top level of the repo.

To start the app, with the Docker engine running, run:
```
docker-compose up
```

Containers may take around ten mintues to build. Navigate to localhost:8050 to 
enter questions into the app. 

If desired, a fastapi endpoint can be set up on port 8000. Change the "command" 
field in the docker-compose yaml file. It is commented out above the command
that runs Dash. Make sure to comment out the Dash command as well.

Any issues, comment or questions email Adam at adam.conovaloff@analytica.net
