from youtube_transcript_api import YouTubeTranscriptApi
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, DataCollatorForLanguageModeling, Trainer, TrainingArguments
from datasets import load_dataset
import torch

print("Starting script...")
# Provide the YouTube video ID (from the video URL)
video_id = "qXR1PRbSfoA"

try:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    print("Transcript successfully retrieved.")
except Exception as e:
    print(f"Error: {e}")
    transcript = []

print("Combining transcript entries...")
script = "\n".join([entry['text'] for entry in transcript])

# Save the script to a text file
script_path = "comedian_script.txt"
with open(script_path, "w", encoding="utf-8") as f:
    f.write(script)
print("Script saved to:", script_path)

print("Loading dataset from text file...")
dataset = load_dataset("text", data_files={"train": script_path})
print("Dataset loaded:", dataset)

# Load the tokenizer and model
# Consider 'distilgpt2' if you need a smaller model
model_name = "gpt2"
print(f"Loading tokenizer and model: {model_name}")
tokenizer = GPT2TokenizerFast.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Approach 1: Set pad_token to eos_token
tokenizer.pad_token = tokenizer.eos_token

# Tokenize the dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], return_special_tokens_mask=True, truncation=True, max_length=512)

print("Tokenizing dataset...")
tokenized_datasets = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=["text"]
)
print("Tokenization complete. Example:", tokenized_datasets["train"][0])

# Create data collator for language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,
    pad_to_multiple_of=8
)
print("Setting training arguments...")
# Set training arguments
training_args = TrainingArguments(
    output_dir="./fine_tuned_comedian_model",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=3,  # Adjust based on memory
    gradient_accumulation_steps=4,
    save_steps=500,
    save_total_limit=2,
    logging_steps=100,
    # Aligning strategies
    evaluation_strategy="no",  # Changed from "no" to "steps"
    save_strategy="steps",  # Ensuring save and eval strategies match
    load_best_model_at_end=False,  # This now works because both are steps
)

device = torch.device("mps")
model.to(device)

# Create a wrapper around your data_collator
class DebugCollator:
    def __init__(self, base_collator):
        self.base_collator = base_collator

    def __call__(self, features):
        batch = self.base_collator(features)
        # Print the shape of the input_ids tensor
        print("Batch input shape:", batch["input_ids"].shape)
        return batch

# Wrap your existing data_collator
debug_data_collator = DebugCollator(data_collator)

# Prepare trainer
print("Initializing Trainer...")
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    data_collator=debug_data_collator,  # Use the wrapped collator
)

print("Starting training...")
trainer.train()
print("Training complete.")

print("Saving model and tokenizer...")
trainer.save_model("./fine_tuned_comedian_model")
tokenizer.save_pretrained("./fine_tuned_comedian_model")
print("Model saved at ./fine_tuned_comedian_model")

# Example of generating text after training
print("Generating sample text...")
# prompt = "So the other day I was thinking about how hard English is for French speakers..."
# prompt = " What you will never hear in france..."
# prompt = "In France we have a problem with one religion..."
prompt = "So last night I went to a bar in Paris, and I realized something about the French language..."
inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
attention_mask = torch.ones_like(inputs, device=device)
outputs = model.generate(
    inputs,
    max_length=200,
    temperature=0.8,
    top_p=0.9,
    do_sample=True,
    attention_mask=attention_mask
)
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Generated text:\n", generated_text)

# debug = 1

# # Initialize dataset
# dataset = []
#
# # Prepare prompts and completions
# for entry in transcript:
#     joke = entry['text']
#     dataset.append({
#         "prompt": "Write a joke in the style of Gad Elmaleh.",
#         "completion": joke.strip()
#     })
#
# # Save to JSONL
# with open("gad_elmaleh_jokes.jsonl", "w") as f:
#     for item in dataset:
#         f.write(json.dumps(item) + "\n")
#
# print("Dataset saved as gad_elmaleh_jokes.jsonl")
#
# from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments
# from datasets import load_dataset
#
# # Load dataset
# dataset = load_dataset("json", data_files="gad_elmaleh_jokes.jsonl")
#
# # Load pre-trained model and tokenizer
# model = GPT2LMHeadModel.from_pretrained("gpt2")
# tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
# tokenizer.pad_token = tokenizer.eos_token
#
# # Fine-tuning arguments
# training_args = TrainingArguments(
#     output_dir="./results",
#     evaluation_strategy="epoch",
#     learning_rate=5e-5,
#     per_device_train_batch_size=8,
#     num_train_epochs=3,
#     save_steps=10_000,
#     save_total_limit=2,
# )
#
# # Fine-tune
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=dataset["train"],
# )
# trainer.train()
#
# # Load fine-tuned model and tokenizer
# from transformers import GPT2LMHeadModel, GPT2Tokenizer
#
# model = GPT2LMHeadModel.from_pretrained("./results")
# tokenizer = GPT2Tokenizer.from_pretrained("./results")
#
# # Generate a joke
# prompt = "Write a joke in the style of Gad Elmaleh."
# input_ids = tokenizer.encode(prompt, return_tensors="pt")
#
# output = model.generate(input_ids, max_length=50, temperature=0.8, num_return_sequences=1)
# print(tokenizer.decode(output[0], skip_special_tokens=True))


'''
download mp4 - works
'''
# import subprocess
# Specify the video URL
# video_url = "https://www.youtube.com/watch?v=qXR1PRbSfoA"
# output_file = "audio.mp4"
#
# # Command to download audio
# command = [
#     "yt-dlp",
#     "-x",  # Extract audio
#     "--audio-format", "mp3",  # Output format
#     "-o", output_file,  # Output file
#     video_url,
# ]
#
# # Run the command
# subprocess.run(command)
# print(f"Audio downloaded to {output_file}")

'''
opens chrome with the video
'''
# from selenium import webdriver
# from bs4 import BeautifulSoup
#
# # Set up WebDriver
# driver = webdriver.Chrome()
#
# # Navigate to a YouTube video
# video_url = "https://www.youtube.com/watch?v=qXR1PRbSfoA"
# driver.get(video_url)
#
# # Parse the page
# soup = BeautifulSoup(driver.page_source, "html.parser")
#
# # Extract video details
# title = soup.find("meta", property="og:title")["content"]
# views = soup.find("meta", itemprop="interactionCount")["content"]
# channel = soup.find("meta", itemprop="channelId")["content"]
#
# print(f"Title: {title}, Views: {views}, Channel ID: {channel}")
# driver.quit()

# import yt_dlp
#
# # Specify the YouTube video URL
# video_url = "https://www.youtube.com/watch?v=qXR1PRbSfoA"
#
# # Set up yt-dlp options
# ydl_opts = {
#     'quiet': True,  # Suppress console output
#     'extract_flat': True,  # Extract only metadata, no download
# }
#
# # Extract video metadata
# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     video_info = ydl.extract_info(video_url, download=False)
#
# # Access metadata
# title = video_info.get("title")
# views = video_info.get("view_count")
# channel = video_info.get("uploader")
# channel_url = video_info.get("uploader_url")
#
# # Print the extracted details
# print(f"Title: {title}")
# print(f"Views: {views}")
# print(f"Channel: {channel}")
# print(f"Channel URL: {channel_url}")


'''
set up youtube api
'''