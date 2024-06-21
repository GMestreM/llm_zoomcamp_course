## Homework: Introduction

In this homework, we'll learn more about search and use Elastic Search for practice. 

## Q1. Running Elastic 

Run Elastic Search 8.4.3, and get the cluster information. If you run it on localhost, this is how you do it:

```bash
curl localhost:9200
```

What's the `version.build_hash` value?

### Answer

Run command

```bash
docker run -it \
--rm \
--name elasticsearch \
-m 4GB \
-p 9200:9200 \
-p 9300:9300 \
-e "discovery.type=single-node" \
-e "xpack.security.enabled=false" \
docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

Then use `curl http://localhost:9200` so we get

{
  "name" : "7a1ea597eecf",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "rb6voLAJQ2aGX1VLd4iJWA",
  "version" : {
    "number" : "8.4.3",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "42f05b9372a9a4a470db3b52817899b99a76ee73",
    "build_date" : "2022-10-04T07:17:24.662462378Z",
    "build_snapshot" : false,
    "lucene_version" : "9.3.0",
    "minimum_wire_compatibility_version" : "7.17.0",
    "minimum_index_compatibility_version" : "7.0.0"
  },
  "tagline" : "You Know, for Search"
}

The **build_hash** is 42f05b9372a9a4a470db3b52817899b99a76ee73


## Getting the data

Now let's get the FAQ data. You can run this snippet:

```python
import requests 

docs_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1'
docs_response = requests.get(docs_url)
documents_raw = docs_response.json()

documents = []

for course in documents_raw:
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)
```

Note that you need to have the `requests` library:

```bash
pip install requests
```

## Q2. Indexing the data

Index the data in the same way as was shown in the course videos. Make the `course` field a keyword and the rest should be text. 

Don't forget to install the ElasticSearch client for Python:

```bash
pip install elasticsearch
```

Which function do you use for adding your data to elastic?

* `insert`
* `index`
* `put`
* `add`

### Answer

We use `index`:

```python
from tqdm.auto import tqdm

for doc in tqdm(documents):
    es.index(index=index_name, document=doc)
```

(also check [this resource](https://dylancastillo.co/elasticsearch-python/#using-esindex))

## Q3. Searching

Now let's search in our index. 

We will execute a query "How do I execute a command in a running docker container?". 

Use only `question` and `text` fields and give `question` a boost of 4, and use `"type": "best_fields"`.

What's the score for the top ranking result?

* 94.05
* 84.05
* 74.05
* 64.05

Look at the `_score` field.

### Answer

The answer is 84.05. I have used the code below:

```python
user_question = "How do I execute a command in a running docker container?"

search_query = {
    "size": 1,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": user_question,
                    "fields": ["question^4", "text"],
                    "type": "best_fields"
                }
            },
            #"filter": {
            #    "term": {
            #        "course": "data-engineering-zoomcamp"
            #    }
            #}
        }
    }
}

response = es_client.search(index=index_name, body=search_query)

for hit in response['hits']['hits']:
    score = hit['_score']
    print(score)

# >> 84.050095
```

(I do not perform any filtering as the question does not ask for this)


## Q4. Filtering

Now let's only limit the questions to `machine-learning-zoomcamp`.

Return 3 results. What's the 3rd question returned by the search engine?

* How do I debug a docker container?
* How do I copy files from a different folder into docker container’s working directory?
* How do Lambda container images work?
* How can I annotate a graph?

### Answer

The answer is `How do I copy files from a different folder into docker container’s working directory?`. The code that I used is this:

```python
user_question = "How do I execute a command in a running docker container?"

search_query = {
    "size": 3,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": user_question,
                    "fields": ["question^4", "text"],
                    "type": "best_fields"
                }
            },
            "filter": {
                "term": {
                    "course": "machine-learning-zoomcamp"
                }
            }
        }
    }
}

response = es_client.search(index=index_name, body=search_query)

for i, hit in enumerate(response['hits']['hits']):
    doc = hit['_source']
    print(f"\n{i}. Question: {doc['question']}")

# >> 0. Question: How do I debug a docker container?
# >> 1. Question: How do I copy files from my local machine to docker container?
# >> 2. Question: How do I copy files from a different folder into docker container’s working directory?
```

## Q5. Building a prompt

Now we're ready to build a prompt to send to an LLM. 

Take the records returned from Elasticsearch in Q4 and use this template to build the context. Separate context entries by two linebreaks (`\n\n`)
```python
context_template = """
Q: {question}
A: {text}
""".strip()
```

Now use the context you just created along with the "How do I execute a command in a running docker container?" question 
to construct a prompt using the template below:

```
prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()
```

What's the length of the resulting prompt? (use the `len` function)

* 962
* 1462
* 1962
* 2462

### Answer

The answer is `1462`. The code I used is the following:

```python
context = ""
for hit in response['hits']['hits']:
    doc = hit['_source']
    question_doc = doc['question']
    text_doc = doc['text']

    context_doc = f"""
Q: {question_doc}
A: {text_doc}
""".strip()

    context = context + context_doc + "\n\n"

# Remove last double linebreak
context = context[:-2]
print(context)

prompt_template = f"""
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {user_question}

CONTEXT:
{context}
""".strip()

print(prompt_template)

# You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
# Use only the facts from the CONTEXT when answering the QUESTION.
# 
# QUESTION: How do I execute a command in a running docker container?
# 
# CONTEXT:
# Q: How do I debug a docker container?
# A: Launch the container image in interactive mode and overriding the entrypoint, so that it starts a bash command.
# docker run -it --entrypoint bash <image>
# If the container is already running, execute a command in the specific container:
# docker ps (find the container-id)
# docker exec -it <container-id> bash
# (Marcos MJD)
# 
# Q: How do I copy files from my local machine to docker container?
# A: You can copy files from your local machine into a Docker container using the docker cp command. Here's how to do it:
# To copy a file or directory from your local machine into a running Docker container, you can use the `docker cp # command`. The basic syntax is as follows:
# docker cp /path/to/local/file_or_directory container_id:/path/in/container
# Hrithik Kumar Advani
# 
# Q: How do I copy files from a different folder into docker container’s working directory?
# A: You can copy files from your local machine into a Docker container using the docker cp command. Here's how to do it:
# In the Dockerfile, you can provide the folder containing the files that you want to copy over. The basic syntax is as follows:
# COPY ["src/predict.py", "models/xgb_model.bin", "./"]											Gopakumar Gopinathan

len(prompt_template)

# >> 1462
```

## Q6. Tokens

When we use the OpenAI Platform, we're charged by the number of 
tokens we send in our prompt and receive in the response.

The OpenAI python package uses `tiktoken` for tokenization:

```bash
pip install tiktoken
```

Let's calculate the number of tokens in our query: 

```python
encoding = tiktoken.encoding_for_model("gpt-4o")
```

Use the `encode` function. How many tokens does our prompt have?

* 122
* 222
* 322
* 422

Note: to decode back a token into a word, you can use the `decode_single_token_bytes` function:

```python
encoding.decode_single_token_bytes(63842)
```

### Answer

The answer is 322. I have used the code below (also see [this tutorial](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken)):

```python
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o")
num_tokens = len(encoding.encode(prompt_template))
num_tokens
# >> 332
```

## Bonus: generating the answer (ungraded)

Let's send the prompt to OpenAI. What's the response?  

Note: you can replace OpenAI with Ollama. See module 2.

## Bonus: calculating the costs (ungraded)

Suppose that on average per request we send 150 tokens and receive back 250 tokens.

How much will it cost to run 1000 requests?

You can see the prices [here](https://openai.com/api/pricing/)

On June 17, the prices for gpt4o are:

* Input: $0.005 / 1K tokens
* Output: $0.015 / 1K tokens

You can redo the calculations with the values you got in Q6 and Q7.


## Submit the results

* Submit your results here: https://courses.datatalks.club/llm-zoomcamp-2024/homework/hw1
* It's possible that your answers won't match exactly. If it's the case, select the closest one.