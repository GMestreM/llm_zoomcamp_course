## Homework: Vector Search

In this homework, we'll experiemnt with vector with and without Elasticsearch

> It's possible that your answers won't match exactly. If it's the case, select the closest one.


## Q1. Getting the embeddings model

First, we will get the embeddings model `multi-qa-distilbert-cos-v1` from
[the Sentence Transformer library](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html#model-overview)

```bash
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer(model_name)
```

Create the embedding for this user question:

```python
user_question = "I just discovered the course. Can I still join it?"
```

What's the first value of the resulting vector?

* -0.24
* -0.04
* 0.07
* 0.27

## Answer

```python
model_name = "multi-qa-distilbert-cos-v1"
embedding_model = SentenceTransformer(model_name)

user_question = "I just discovered the course. Can I still join it?"
embedding = embedding_model.encode(user_question)
embedding[0]

## >> 0.07822264
```

The first value of the resulting embedding vector is `0.07`


## Prepare the documents

Now we will create the embeddings for the documents.

Load the documents with ids that we prepared in the module:

```python
import requests 

base_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main'
relative_url = '03-vector-search/eval/documents-with-ids.json'
docs_url = f'{base_url}/{relative_url}?raw=1'
docs_response = requests.get(docs_url)
documents = docs_response.json()
```

We will use only a subset of the questions - the questions
for `"machine-learning-zoomcamp"`. After filtering, you should
have only 375 documents


```python
# Filter documents belonging to machine-learning-zoomcamp
course_filter = "machine-learning-zoomcamp"
filtered_documents = []
for document in documents:
    if document["course"] == course_filter:
        filtered_documents.append(document)

# Check that there are only 375 documents
del documents
len(filtered_documents)
## >> 375
```

## Q2. Creating the embeddings

Now for each document, we will create an embedding for both question and answer fields.

We want to put all of them into a single matrix `X`:

- Create a list `embeddings` 
- Iterate over each document 
- `qa_text = f'{question} {text}'`
- compute the embedding for `qa_text`, append to `embeddings`
- At the end, let `X = np.array(embeddings)` (`import numpy as np`) 

What's the shape of X? (`X.shape`). Include the parantheses. 

## Answer

```python
embeddings = []
for document in tqdm(filtered_documents):
    question = document["question"]
    text = document["text"]
    qa_text = f"{question} {text}"

    # Compute embedding
    embeddings.append(embedding_model.encode(qa_text))

X = np.array(embeddings)
X.shape
## >> (375, 768)
```

Shape of `X` is `(375, 768)`

## Q3. Search

We have the embeddings and the query vector. Now let's compute the 
cosine similarity between the vector from Q1 (let's call it `v`) and the matrix from Q2. 

The vectors returned from the embedding model are already
normalized (you can check it by computing a dot product of a vector
with itself - it should return something very close to 1.0). This means that in order
to compute the coside similarity, it's sufficient to 
multiply the matrix `X` by the vector `v`:


```python
scores = X.dot(v)
```

What's the highest score in the results?

- 65.0 
- 6.5
- 0.65
- 0.065

## Answer

```python
scores = X.dot(v)
np.max(scores)
## >> 0.6506573
```

The highest score in the results is `0.65`


## Vector search

We can now compute the similarity between a query vector and all the embeddings.

Let's use this to implement our own vector search

```python
class VectorSearchEngine():
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.embeddings = embeddings

    def search(self, v_query, num_results=10):
        scores = self.embeddings.dot(v_query)
        idx = np.argsort(-scores)[:num_results]
        return [self.documents[i] for i in idx]

search_engine = VectorSearchEngine(documents=documents, embeddings=X)
search_engine.search(v, num_results=5)
```

If you don't understand how the `search` function work:

* Ask ChatGTP or any other LLM of your choice to explain the code
* Check our pre-course workshop about implementing a search engine [here](https://github.com/alexeygrigorev/build-your-own-search-engine)

(Note: you can replace `argsort` with `argpartition` to make it a lot faster)


## Q4. Hit-rate for our search engine

Let's evaluate the performance of our own search engine. We will
use the hitrate metric for evaluation.

First, load the ground truth dataset:

```python
import pandas as pd

base_url = 'https://github.com/DataTalksClub/llm-zoomcamp/blob/main'
relative_url = '03-vector-search/eval/ground-truth-data.csv'
ground_truth_url = f'{base_url}/{relative_url}?raw=1'

df_ground_truth = pd.read_csv(ground_truth_url)
df_ground_truth = df_ground_truth[df_ground_truth.course == 'machine-learning-zoomcamp']
ground_truth = df_ground_truth.to_dict(orient='records')
```

Now use the code from the module to calculate the hitrate of
`VectorSearchEngine` with `num_results=5`.

What did you get?

* 0.93
* 0.73
* 0.53
* 0.33

## Answer

```python
hit_rate = []

for question_document in tqdm(ground_truth):

    # Get question embedding
    question_embedding = embedding_model.encode(question_document["question"])

    # Search using our own engine
    results = search_engine.search(question_embedding, num_results=5)

    # Check if the id of our ground-truth question matches with any id of the documents retrieved
    contain_document = question_document["document"] in [
        result["id"] for result in results
    ]
    hit_rate.append(contain_document)

np.mean(hit_rate)
## >> 0.9398907103825137
```

The hit-rate for our search engine (`VectorSearchEngine` with `num_results=5`) is `0.93`

## Q5. Indexing with Elasticsearch

Now let's index these documents with elasticsearch

* Create the index with the same settings as in the module (but change the dimensions)
* Index the embeddings (note: you've already computed them)

After indexing, let's perform the search of the same query from Q1.

What's the ID of the document with the highest score?

## Answer

First we need to run elasticsearch in a container using this command

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

```python
# Now connect to elasticsearch
es_client = Elasticsearch("http://localhost:9200")

# Create index
index_settings = {
    "settings": {"number_of_shards": 1, "number_of_replicas": 0},
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"},
            "id": {"type": "keyword"},
            "question_vector": {
                "type": "dense_vector",
                "dims": 768,
                "index": True,
                "similarity": "cosine",
            },
        }
    },
}

index_name = "course-questions"

es_client.indices.delete(index=index_name, ignore_unavailable=True)
es_client.indices.create(index=index_name, body=index_settings)

# Append embedding to documents
for idx, document in enumerate(filtered_documents):
    document["question_vector"] = X[idx, :]

# Index documents and embeddings
for doc in tqdm(filtered_documents):
    es_client.index(index=index_name, document=doc)

# Search for the question of Q1 using elasticsearch
def elastic_search_knn(field: str, vector: np.array):
    knn = {
        "field": field,
        "query_vector": vector,
        "k": 5,
        "num_candidates": 10000,
    }

    search_query = {
        "knn": knn,
        "_source": ["text", "section", "question", "course", "id"],
    }

    es_results = es_client.search(index=index_name, body=search_query)

    result_docs = []

    for hit in es_results["hits"]["hits"]:
        result_docs.append(hit["_source"])

    return result_docs

result_docs = elastic_search_knn(field="question_vector", vector=v)
result_docs[0]

# {'question': 'The course has already started. Can I still join it?',
#  'course': 'machine-learning-zoomcamp',
#  'section': 'General course-related questions',
#  'text': 'Yes, you can. You won’t be able to submit some of the homeworks, but you can still take part in the course.\nIn order to get a certificate, you need to submit 2 out of 3 course projects and review 3 peers’ Projects by the deadline. It means that if you join the course at the end of November and manage to work on two projects, you will still be eligible for a certificate.',
# 'id': 'ee58a693'}
```

The ID of the document with the highest score is `ee58a693`

## Q6. Hit-rate for Elasticsearch

The search engine we used in Q4 computed the similarity between
the query and ALL the vectors in our database. Usually this is 
not practical, as we may have a lot of data.

Elasticsearch uses approximate techniques to make it faster. 

Let's evaluate how worse the results are when we switch from
exact search (as in Q4) to approximate search with Elastic.

What's hitrate for our dataset for Elastic?

* 0.93
* 0.73
* 0.53
* 0.33

## Answer

```python
hit_rate_es = []

for question_document in tqdm(ground_truth):

    # Get question embedding
    question_embedding = embedding_model.encode(question_document["question"])

    # Search using our elasticsearch
    results = elastic_search_knn(field="question_vector", vector=question_embedding)

    # Check if the id of our ground-truth question matches with any id of the documents retrieved
    contain_document = question_document["document"] in [
        result["id"] for result in results
    ]
    hit_rate_es.append(contain_document)

np.mean(hit_rate_es)
## >> 0.9398907103825137
```

## Submit the results

* Submit your results here: https://courses.datatalks.club/llm-zoomcamp-2024/homework/hw3
* It's possible that your answers won't match exactly. If it's the case, select the closest one.