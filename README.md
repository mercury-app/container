# Mercury container

Container for handling events inside mercury node containers.

### Usage

### Build docker image

```sh
docker build . -t jupyter-mercury:latest
```

The interaction with this is done via python cli as this will usually be called using `docker exec` commands. 

1. Create a new notebook inside container.

```
python3 -m container.cli create-notebook --name Untitled.ipynb
```

2. Execute code inside the running jupyter kernel of the container.

```
python3 -m container.cli execute-code --code "a+b"
```

The code is run inside the already running jupyter kernel so it can- 
- Access all objects created in the running kernel.
- Create new objects inside the running kernel/