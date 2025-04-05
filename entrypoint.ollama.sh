#!/bin/sh
# Start Ollama server in the background
ollama serve &

# Wait for it to start up
sleep 5

# Pull the models
ollama pull nomic-embed-text
ollama pull deepseek-r1:8b
ollama pull gemma3

# Wait so container doesn't exit
wait
