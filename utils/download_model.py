from transformers import AutoTokenizer, AutoModelForSequenceClassification

local_dir = "./models/multilingual-sentiment"

# Model name
model_name = "tabularisai/multilingual-sentiment-analysis"

# Download tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=local_dir)

# Download model weights
model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=local_dir)

print("✅ The model download is completed and has been cached locally.")
