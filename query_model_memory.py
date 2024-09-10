from mem0 import Memory


llm_provider = "ollama"
model_name = "llama3.1:8b-instruct-fp16"
openai_base_url = "http://localhost:18888/v1/"
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "lishen——0830",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 768,  # Change this according to your local model's dimensions
        },
    },
     "llm": {
        "provider": llm_provider,
        "config": {
            "model": model_name,
            "top_p":0.95,
            "temperature":0.5,
            # "openai_base_url":  openai_base_url
            "ollama_base_url": "http://localhost:11434",
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text:latest",
            # Alternatively, you can use "snowflake-arctic-embed:latest"
            "ollama_base_url": "http://localhost:11434",
        },
    },
    "version": "v1.1"
}

m = Memory.from_config(config)
# m.reset()
all_memories = m.get_all()

print("all_memories",all_memories) 
for memory in all_memories['memories']:

    memory_id = memory["id"] # get a memory_id
    print(memory_id)
    history = m.history(memory_id=memory_id)
    print(history)



        