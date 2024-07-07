    ## Homework: Vector Search

    In this homework, we'll implement an end to end semantic search engine

    > It's possible that your answers won't match exactly. If it's the case, select the closest one.

    ## Q1. Prepare Documents

    Import documents.json, read the file and prepare the dataset:

    ```bash
    import json

    with open('documents.json', 'rt') as f_in:
        docs_raw = json.load(f_in)

    documents = []

    for course_dict in docs_raw:
        for doc in course_dict['documents']:
            doc['course'] = course_dict['course']
            documents.append(doc)

    len(documents)
    ```
    How many records we have in the pre-processed "documents"?
    * 1000
    * 1051
    * 901
    * 948


### Answer

If we follow those instructions, we obtain a lenght of `948`.

To download file `documents.json` (stored in `https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1`) we execute this command in the terminal (located on the root folder of the project)

```bash
wget -c https://github.com/DataTalksClub/llm-zoomcamp/blob/main/01-intro/documents.json?raw=1 -O data/documents.json
```

## Q2. Create Embeddings using Pretrained Models

Import sentence transformer library. Please review the Sentence Transformer pretrained documentation here: https://www.sbert.net/docs/sentence_transformer/pretrained_models.html#model-overview

```bash
# This is a new library compared to the previous modules. 
# Please perform "pip install sentence_transformers==2.7.0"

from sentence_transformers import SentenceTransformer

# if you get an error do the following:
# 1. Uninstall numpy 
# 2. Uninstall torch
# 3. pip install numpy==1.26.4
# 4. pip install torch
# run the above cell, it should work
model = SentenceTransformer("all-MiniLM-L12-v2")
```

What is the model size (in MB) and average performance?

* [420, 63.30]
* [120, 59.76]
* [290, 59.84]
* [420, 51.72]

### Answer

If we go to the [Sentence Transformer documentation] and search for `all-MiniLM-L12-v2` we can see that the model size is `120 MB` and its average performance is `59.76`. So the answer is `[120, 59.76]`

## Q3. Get the dimension for model embedding

```bash
len(model.encode("This is a simple sentence"))
```

What is the dimension of the model embedding?

* 768
* 265
* 384
* 1056

```bash
#created the dense vector using the pre-trained model
operations = []
for doc in documents:
    # Transforming the title into an embedding using the model
    doc["question_vector"] = model.encode(doc["question"]).tolist()
    operations.append(doc)
```


Establish connection to Elasticsearch 

```bash
from elasticsearch import Elasticsearch
es_client = Elasticsearch('http://localhost:9200') 

es_client.info()
```

### Answer

```python
model = SentenceTransformer("all-MiniLM-L12-v2")
len(model.encode("This is a simple sentence"))
# >> 384
```

The answer is `384`

## Q4: Create Mappings and Index

In the mappings, change "section" to "keyword" type

```bash
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "keyword"},
            "question": {"type": "text"},
            "course": {"type": "keyword"} ,
            "question_vector":{"type":"dense_vector","dims": 384,"index":True,"similarity": "cosine"
        },
        }
    }
}

index_name = "course-questions"

es_client.indices.delete(index=index_name, ignore_unavailable=True)
es_client.indices.create(index=index_name, body=index_settings)
```

Add documents into index

```bash
for doc in operations:
    try:
        es_client.index(index=index_name, document=doc)
    except Exception as e:
        print(e)
```

In the es_client.indices.delete statement, what does "ignore_unavailable" mean?
* If the pre-trained model in unavailable, skip this statement
* If the index is unavailable, skip this statement
* If the pre-trained model in unavailable, don't skip this statement
* If the index is unavailable, don't skip this statement


### Answer

As stated in [this course video](https://youtu.be/ptByfB_YcEg?si=cXt0NnN5DkLkvmcL&t=1023), including parameter `ignore_unavailable=True` means that if the index we are trying to delete doesn't exists, that statement will be skipped.

The answer is `If the index is unavailable, skip this statement`


## Q5: Create end user query and perform semantic search

Use the search term "how to enrol to course?" and perform semantic search

```bash
search_term = "how to enrol to course?"
vector_search_term = model.encode(search_term)

query = {
    "field" : "question_vector",
    "query_vector" :  vector_search_term,
    "k" : 5,
    "num_candidates" : 10000, 
}

res = es_client.search(index=index_name, knn=query,source=["text","section","question","course"])
res["hits"]["hits"]
```
What is the similarity score, section and course for the first result?

* [0.78, 'Module 1: Introduction', 'mlops-zoomcamp']
* [0.74, 'General course-related questions', 'data-engineering-zoomcamp']
* [0.72, 'Projects (Midterm and Capstone)', 'machine-learning-zoomcamp']
* [0.71, 'General course-related questions', 'machine-learning-zoomcamp']

### Answer

```python
search_term = "how to enrol to course?"
vector_search_term = model.encode(search_term)

query = {
    "field" : "question_vector",
    "query_vector" :  vector_search_term,
    "k" : 5,
    "num_candidates" : 10000, 
}

res = es_client.search(index=index_name, knn=query,source=["text","section","question","course"])
#Just show first result
res["hits"]["hits"][0]
```

```json
{'_index': 'course-questions',
 '_id': 'wAXsjZAB9_D20czfcmBV',
 '_score': 0.852048,
 '_source': {'question': 'Course - What are the prerequisites for this course?',
  'course': 'data-engineering-zoomcamp',
  'section': 'General course-related questions',
  'text': 'GitHub - DataTalksClub data-engineering-zoomcamp#prerequisites'}}
```

### Answer 

For the first results, the similarity score obtained is `0.852048`, the section is `General course-related questions` and the course is `data-engineering-zoomcamp`

Among these four choices
* [0.78, 'Module 1: Introduction', 'mlops-zoomcamp']
* [0.74, 'General course-related questions', 'data-engineering-zoomcamp']
* [0.72, 'Projects (Midterm and Capstone)', 'machine-learning-zoomcamp']
* [0.71, 'General course-related questions', 'machine-learning-zoomcamp']

The closest one is `[0.74, 'General course-related questions', 'data-engineering-zoomcamp']` (although the similarity score does not match)

## Q6: Perform Semantic Search & Filtering

Filter the results to "General course-related questions" section only

```bash
knn_query = {
    "field" : "text_vector",
    "query_vector" :  vector_search_term,
    "k" : 5,
    "num_candidates" : 10000
}

response = es_client.search(
    index=index_name,
    query={
        "match": {
                "section": "General course-related questions"
            },
        },
        
    knn=knn_query,
    size=5
)

response["hits"]["hits"]
```
Do you see the results filtered only to "General course-related questions" section?

* Yes
* No

### Answer

An error has been found in the homework (7th July 2024, 16:01 GMT)

The statement of this question says to use this query:
```python
knn_query = {
    "field" : "text_vector",
    "query_vector" :  vector_search_term,
    "k" : 5,
    "num_candidates" : 10000
}
```

but in this lab we haven't got any embedding for `text_vector` (it does not appear in the elastic search mapping). Hence, I have changed it to `question_vector`, as it's the only embedding we have:

```python
knn_query = {
    "field" : "question_vector", # it has been changed, in statement is said "text_vector", but we haven't got any embedding for that field!
    "query_vector" :  vector_search_term,
    "k" : 5,
    "num_candidates" : 10000
}
```

After running the rest of the code, we see that all 5 top documents are from section `'General course-related questions'`, hence the answer is `Yes`.

## Submit the results

* Submit your results here: https://courses.datatalks.club/llm-zoomcamp-2024/homework/hw3 (to be created)
* It's possible that your answers won't match exactly. If it's the case, select the closest one.