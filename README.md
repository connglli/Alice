# Alice

Alice is an [Auto-GPT](https://github.com/Torantulino/Auto-GPT) re-implementation which replaces OpenAI with Quora's Poe and Microsoft's New Bing, and perhaps other domain models.


## Requirements

- Python 3.8 or later
- New Bing cookies
- Poe `p-b` cookie


## Installation

To install Alice, follow these steps:

0. Make sure you have all the requirements above, if not, install/get them.

1. Clone the repository:

   ```
   git clone https://github.com/connglli/Alice.git
   ```

2. Install the required dependencies:

   ```
   cd 'Alice'
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Rename `.env.template` to `.env` and fill in your `NEW_BING_COOKIES_PATH` and `POE_P_B_COOKIE_TOKEN`. Check [EdgeGPT](https://github.com/acheong08/EdgeGPT) and [poe-api](https://github.com/ading2210/poe-api) on how to fetch them.

4. *Optional*. Install pre-commit for git:

   ```
   pre-commit install
   ```

## Usage

1. Run the `main.py`:

   ```
   python scripts/main.py
   ```

2. After each of Alice's action, type "NEXT COMMAND" to authorise them to continue.

3. To exit the program, type "exit" and press Enter.

4. For other options like "speech", "memory", "debug", check [Auto-GPT](https://github.com/Torantulino/Auto-GPT)


## Issues

- New Bing is slow, seems even slower than OpenAI API.
- New Bing's ability is restricted by Microsoft. It often performs worse than GPT3.5 and GPT4.
- New Bing sometimes doesn't respond anything.
- Poe's token sometimes get expired. See [this issue](https://github.com/ading2210/poe-api/issues/14).


## TODO

- Dynamic chatbot allocation and reclamation. Check [this comment](https://github.com/ading2210/poe-api/issues/34#issuecomment-1501803552).
- Login Poe via email and verification code. Check [this issue](https://github.com/ading2210/poe-api/issues/31).
- More system tests.
- Remove New Bing.
- Add domain models like [Jarvis/HuggingGPT](https://github.com/microsoft/JARVIS/blob/main/CITATION.cff) when performing specific tasks like text summarization.


## Thanks

- [Auto-GPT](https://github.com/Torantulino/Auto-GPT)
- [EdgeGPT](https://github.com/acheong08/EdgeGPT)
- [poe-api](https://github.com/ading2210/poe-api)
