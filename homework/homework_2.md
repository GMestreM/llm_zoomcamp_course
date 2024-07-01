## Homework: Open-Source LLMs

In this homework, we'll experiment more with Ollama

> It's possible that your answers won't match exactly. If it's the case, select the closest one.

## Q1. Running Ollama with Docker

Let's run ollama with Docker. We will need to execute the 
same command as in the lectures:

```bash
docker run -it \
    --rm \
    -v ollama:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama
```

What's the version of ollama client? 

To find out, enter the container and execute `ollama` with the `-v` flag.

### Answer

In order to enter the container we will execute this in the terminal:

```bash
docker exec -it ollama bash
```

Once we are inside the container, we can use 

```bash
ollama -v
```

We obtain the following version of Ollama

```bash
ollama version is 0.1.48
```


## Q2. Downloading an LLM 

We will donwload a smaller LLM - gemma:2b. 

Again let's enter the container and pull the model:

```bash
ollama pull gemma:2b
```

In docker, it saved the results into `/root/.ollama`

We're interested in the metadata about this model. You can find
it in `models/manifests/registry.ollama.ai/library`

What's the content of the file related to gemma?

### Answer

Inside the docker container, let's navigate to `/root/.ollama`

```bash
cd root/.ollama/
ls -l
>> id_ed25519  id_ed25519.pub  models
```

Now let's dive in the path specified by the question:

```bash
cd models/manifests/registry.ollama.ai/library
```

The elements inside that directory are

```bash
ls -l
>> total 4
>> drwxr-xr-x 2 root root 4096 Jul  1 19:47 gemma
```

If we go inside directory `gemma` we get:

```bash
cd gemma
ls -l
>> -rw-r--r-- 1 root root 856 Jul  1 19:47 2b
```

```bash
cat 2b
>> {
  "schemaVersion": 2,
  "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
  "config": {
    "mediaType": "application/vnd.docker.container.image.v1+json",
    "digest": "sha256:887433b89a901c156f7e6944442f3c9e57f3c55d6ed52042cbb7303aea994290",
    "size": 483
  },
  "layers": [
    {
      "mediaType": "application/vnd.ollama.image.model",
      "digest": "sha256:c1864a5eb19305c40519da12cc543519e48a0697ecd30e15d5ac228644957d12",
      "size": 1678447520
    },
    {
      "mediaType": "application/vnd.ollama.image.license",
      "digest": "sha256:097a36493f718248845233af1d3fefe7a303f864fae13bc31a3a9704229378ca",
      "size": 8433
    },
    {
      "mediaType": "application/vnd.ollama.image.template",
      "digest": "sha256:109037bec39c0becc8221222ae23557559bc594290945a2c4221ab4f303b8871",
      "size": 136
    },
    {
      "mediaType": "application/vnd.ollama.image.params",
      "digest": "sha256:22a838ceb7fb22755a3b0ae9b4eadde629d19be1f651f73efb8c6b4e2cd0eea0",
      "size": 84
    }
  ]
}
```

## Q3. Running the LLM

Test the following prompt: "10 * 10". What's the answer?

### Answer

In the docker terminal, we can execute this command

```bash
ollama run gemma:2b
>>> 10*10
> Sure, here is the answer:

> 10 * 10 = 100
```

If we run it again, we get a quite similar (but different) answer

```bash
>>> 10*10
> The answer is 100.
```

## Q4. Donwloading the weights 

We don't want to pull the weights every time we run
a docker container. Let's do it once and have them available
every time we start a container.

First, we will need to change how we run the container.

Instead of mapping the `/root/.ollama` folder to a named volume,
let's map it to a local directory:

```bash
mkdir ollama_files

docker run -it \
    --rm \
    -v ./ollama_files:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama
```

Now pull the model:

```bash
docker exec -it ollama ollama pull gemma:2b 
```

What's the size of the `ollama_files/models` folder? 

* 0.6G
* 1.2G
* 1.7G
* 2.2G

Hint: on linux, you can use `du -h` for that.

### Answer

We exit the docker container and go back to our own system. We create a local directory using

```bash
mkdir ollama_files
```

Then, we have to stop the actual docker container using

```bash
docker stop ollama
docker ps
> CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

Once stopped, we can execute the following docker build command:

```bash
docker run -it \
    --rm \
    -v ./ollama_files:/root/.ollama \
    -p 11434:11434 \
    --name ollama \
    ollama/ollama
```

Finally, following the instructions we pull the model

```bash
docker exec -it ollama ollama pull gemma:2b 
```

Once downloaded, let's check the size of the `ollama_files/models` folder:

```bash
du -h ./ollama_files/models/
> 8.0K    ./ollama_files/models/manifests/registry.ollama.ai/library/gemma
> 12K     ./ollama_files/models/manifests/registry.ollama.ai/library
> 16K     ./ollama_files/models/manifests/registry.ollama.ai
> 20K     ./ollama_files/models/manifests
> 1.6G    ./ollama_files/models/blobs
> 1.6G    ./ollama_files/models/
```

So the size of the `ollama_files/models` is 1.6G (the closest option is 1.7G)

## Q5. Adding the weights

Let's now stop the container and add the weights 
to a new image

For that, let's create a `Dockerfile`:

```dockerfile
FROM ollama/ollama

COPY ...
```

What do you put after `COPY`?

### Answer

First let's stop the container

```bash
docker stop ollama
docker ps
> CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

Then, we create a `Dockerfile` in this repository. We want to copy the content of the local directory `ollama_files` in the container's directory `root/.ollama/`. Hence, our `Dockerfile` will be 

```dockerfile
FROM ollama/ollama

COPY ./ollama_files root/.ollama/
```

Now let's built the image.

## Q6. Serving it 

Let's build it:

```bash
docker build -t ollama-gemma2b .
```

And run it:

```bash
docker run -it --rm -p 11434:11434 ollama-gemma2b
```

We can connect to it using the OpenAI client

Let's test it with the following prompt:

```python
prompt = "What's the formula for energy?"
```

Also, to make results reproducible, set the `temperature` parameter to 0:

```bash
response = client.chat.completions.create(
    #...
    temperature=0.0
)
```

How many completion tokens did you get in response?

* 304
* 604
* 904
* 1204

### Answer

Once we have created our `Dockerfile`, we build the image using 

```bash
docker build -t ollama-gemma2b .
```

Once finished, we execute the new container `ollama-gemma2b`:

```bash
docker run -it --rm -p 11434:11434 ollama-gemma2b
```

Ollama will be running on port `11434`. Now we will create a Python script (`scripts/connect_ollama.py`) that will connect to this Ollama instance and submit a prompt.

The entire script is as follows:

```python
from openai import OpenAI

if __name__ == '__main__':
    # Open connection to Ollama using OpenAI client
    client = OpenAI(
        base_url='http://localhost:11434/v1/',
        api_key='ollama',
    )
    
    prompt = "What's the formula for energy?"

    
    response = client.chat.completions.create(
        model='gemma:2b',
        temperature=0.0, # set temperature parameter to 0
        messages=[{"role": "user", "content": prompt}],
    )

    print(response.choices[0].message.content)
    print('\n\nEND PROMPT\n\n')
    
    for r in response:
        print(r)
    
    # ('id', 'chatcmpl-538')
    # ('choices', [Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content="Sure, here's the formula for energy:\n\n**E = K + U**\n\nWhere:\n\n* **E** is the energy in joules (J)\n* **K** is the kinetic energy in joules (J)\n* **U** is the potential energy in joules (J)\n\n**Kinetic energy (K)** is the energy an object possesses when it moves or is in motion. It is calculated as half the product of an object's mass (m) and its velocity (v) squared:\n\n**K = 1/2 * m * v^2**\n\n**Potential energy (U)** is the energy an object possesses when it is in a position or has a specific configuration. It is calculated as the product of an object's mass and the gravitational constant (g) multiplied by the height or distance of the object from a reference point.\n\n**Gravitational potential energy (U)** is given by the formula:\n\n**U = mgh**\n\nWhere:\n\n* **m** is the mass of the object in kilograms (kg)\n* **g** is the acceleration due to gravity in meters per second squared (m/s^2)\n* **h** is the height or distance of the object in meters (m)\n\nThe formula for energy can be used to calculate the total energy of an object, the energy of a specific part of an object, or the change in energy of an object over time.", role='assistant', function_call=None, tool_calls=None))])
    # ('created', 1719865480)
    # ('model', 'gemma:2b')
    # ('object', 'chat.completion')
    # ('service_tier', None)
    # ('system_fingerprint', 'fp_ollama')
    # ('usage', CompletionUsage(completion_tokens=304, prompt_tokens=0, total_tokens=304))
```

So the completion_tokens are 304.

### Annex

This is the answer that I got from the LLM:

```
Sure, here's the formula for energy:

**E = K + U**

Where:

* **E** is the energy in joules (J)
* **K** is the kinetic energy in joules (J)
* **U** is the potential energy in joules (J)

**Kinetic energy (K)** is the energy an object possesses when it moves or is in motion. It is calculated as half the product of an object's mass (m) and its velocity (v) squared:

**K = 1/2 * m * v^2**

**Potential energy (U)** is the energy an object possesses when it is in a position or has a specific configuration. It is calculated as the product of an object's mass and the gravitational constant (g) multiplied by the height or distance of the object from a reference point.

**Gravitational potential energy (U)** is given by the formula:

**U = mgh**

Where:

* **m** is the mass of the object in kilograms (kg)
* **g** is the acceleration due to gravity in meters per second squared (m/s^2)
* **h** is the height or distance of the object in meters (m)

The formula for energy can be used to calculate the total energy of an object, the energy of a specific part of an object, or the change in energy of an object over time.
```

And these are the results of doing the `docker build`:

```
[+] Building 18.4s (7/7) FINISHED                                                                                                                docker:default
 => [internal] load build definition from Dockerfile                                                                                                       0.0s
 => => transferring dockerfile: 90B                                                                                                                        0.0s
 => [internal] load metadata for docker.io/ollama/ollama:latest                                                                                            0.0s
 => [internal] load .dockerignore                                                                                                                          0.1s
 => => transferring context: 2B                                                                                                                            0.0s
 => [internal] load build context                                                                                                                          6.4s
 => => transferring context: 1.68GB                                                                                                                        5.7s
 => [1/2] FROM docker.io/ollama/ollama:latest                                                                                                              0.3s
 => [2/2] COPY ./ollama_files root/.ollama/                                                                                                                8.4s
 => exporting to image                                                                                                                                     3.1s
 => => exporting layers                                                                                                                                    3.0s
 => => writing image sha256:4cbe09451cac1097acc73118c97ab3a5cce07b04ef8d247af89ece642492de28                                                               0.0s
 => => naming to docker.io/library/ollama-gemma2b  
```

## Submit the results

* Submit your results here: https://courses.datatalks.club/llm-zoomcamp-2024/homework/hw2
* It's possible that your answers won't match exactly. If it's the case, select the closest one.