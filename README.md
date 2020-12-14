# Setup your environment

You will need to set up an appropriate coding environment on whatever computer
you expect to use for this assignment.
Minimally, you will need:
 
* [git](https://git-scm.com/downloads/)
* [Docker desktop] (https://www.docker.com/products/docker-desktop)
* [Python (3.8 or higher)](https://www.python.org/)
* [Lupyne](https://pypi.org/project/lupyne/)
* [SpaCy] (https://spacy.io/) 


# Create a new docker container

To downlaod the docker image that contains Python, Lupyne, PyLucene, SpaCy, and index files, please run: 
```
docker pull csc483/pylucene_proj:version1
```
Then, you can start up a new container and connect to it.
```
docker run --name csc483_proj -td csc483/pylucene_proj:version1
docker exec -it csc483_proj bash
```

# Run the code

To run the code, please type the following:
```
python src/main/python/edu/arizona/cs/query_engine.py
```
