# LLM Zoomcamp course notes

This repo contains my course notes for the [LLM Zoomcamp course](https://github.com/DataTalksClub/llm-zoomcamp/)

# Setup
- Test the environment:
    - **Docker**: `docker run hello-world`
    - **Python**: `python -V`
    - **Install Miniconda**:
        - Go to [this repo](https://repo.anaconda.com/miniconda/)
        - Find the latest installation link that ends with `.sh`
        - Copy that link, and in the terminal execute `wget <link>`
        - Open a new terminal, and we should have miniconda installed
    - **Install packages**:
    ```bash
    pip install tqdm notebook==7.1.2 openai elasticsearch scikit-learn pandas shuttleai
    ```
    Then write `requirements.txt` using `pip list --format=freeze > requirements.txt`
    - **Running ElasticSearch**: use this command:
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