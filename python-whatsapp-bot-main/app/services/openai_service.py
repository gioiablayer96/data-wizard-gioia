from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv('/Users/michaelbenmergui/Documents/Gioia/PycharmProjects/data-wizard-gioia/python-whatsapp-bot-main/example.env')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)


def upload_file(path):
    # Upload a file with an "assistants" purpose
    file = client.files.create(
        file=open("../../data/airbnb-faq.pdf", "rb"), purpose="assistants"
    )


def create_assistant(file):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="WhatsApp AirBnb Assistant",
        instructions="You're a helpful WhatsApp assistant that can assist guests that are staying in our Paris AirBnb. Use your knowledge base to best respond to customer queries. If you don't know the answer, say simply that you cannot help with question and advice to contact the host directly. Be friendly and funny.",
        tools=[{"type": "retrieval"}],
        model="gpt-3.5-turbo",
        file_ids=[file.id],
    )
    return assistant


# Use context manager to ensure the shelf file is closed properly
def check_if_thread_exists(wa_id):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wa_id, None)


def store_thread(wa_id, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id


# def run_assistant(thread, name):
#     # Retrieve the Assistant
#     assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)
#
#     # Run the assistant
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id,
#         # instructions=f"You are having a conversation with {name}",
#     )
#
#     # Wait for completion
#     # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
#     while run.status != "completed":
#         # Be nice to the API
#         time.sleep(0.5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
#
#     # Retrieve the Messages
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     new_message = messages.data[0].content[0].text.value
#     logging.info(f"Generated message: {new_message}")
#     return new_message

# def run_assistant(thread):
#     # Retrieve the Assistant
#     assistant = client.beta.assistants.retrieve("asst_PpN6BSGkVlVFq3t653q4NrxX")
#
#     # Run the assistant
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant.id)
#
#     # Wait for completion
#     # https://platform.openai.com/docs/assistants/how-it-works/runs-and-run-steps#:~:text=under%20failed_at.-,Polling%20for%20updates,-In%20order%20to
#     timeout = 30  # seconds
#     start_time = time.time()
#
#     while run.status not in ["completed", "failed"]:
#         if time.time() - start_time > timeout:
#             logging.error("The assistant run timed out.")
#             return "Sorry, I encountered an issue. Please try again."
#         time.sleep(0.5)
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
#
#     if run.status == "failed":
#         logging.error(f"The assistant run failed. Run details: {run}")
#         return "Sorry, I encountered an issue. Please try again."
#
#     # Retrieve the Messages **after this specific run**
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#
#     # Filter assistant messages sent after this run started
#     assistant_messages = [
#         msg for msg in messages.data
#         if msg.run_id == run.id and msg.role == "assistant"
#     ]
#
#     if assistant_messages:
#         new_message = assistant_messages[0].content[0].text.value
#         logging.info(f"Generated message: {new_message}")
#         return new_message
#     else:
#         return "No response from the assistant."

def run_assistant(thread):
    try:
        # Retrieve the Assistant
        assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # Poll for updates with a timeout
        timeout = 30  # seconds
        start_time = time.time()

        while run.status not in ["completed", "failed"]:
            if time.time() - start_time > timeout:
                logging.error("The assistant run timed out.")
                return "Sorry, the assistant took too long to respond. Please try again."
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "failed":
            logging.error(f"The assistant run failed. Run details: {run}")
            return "Sorry, I encountered an issue. Please try again."

        # Retrieve Messages after the run
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Filter assistant messages sent after this run started
        assistant_messages = [
            msg for msg in messages.data
            if msg.run_id == run.id and msg.role == "assistant"
        ]

        if assistant_messages:
            new_message = assistant_messages[0].content[0].text.value
            logging.info(f"Generated message: {new_message}")
            return new_message
        else:
            return "No response from the assistant."

    except Exception as e:
        logging.error(f"An error occurred in run_assistant: {e}")
        return "Sorry, something went wrong."


def generate_response(message_body, wa_id, name):
    # Check if there is already a thread_id for the wa_id
    thread_id = check_if_thread_exists(wa_id)

    print(f'thread_id = {thread_id}')

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating new thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.create()
        store_thread(wa_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")
        thread = client.beta.threads.retrieve(thread_id)

    # Add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Run the assistant and get the new message
    # new_message = run_assistant(thread, name)
    new_message = run_assistant(thread)

    return new_message
