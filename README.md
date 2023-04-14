# Alice

Alice is an [Auto-GPT](https://github.com/Torantulino/Auto-GPT) re-implementation which replaces OpenAI with New Bing and perhaps domain models.


## Requirements

- Python 3.8 or later
- New Bing cookies


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

3. Rename `.env.template` to `.env` and fill in your `NEW_BING_COOKIES_PATH`. Check [EdgeGPT](https://github.com/acheong08/EdgeGPT) on how to fetch your cookies.

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


## TODO

- More tests.
- Check New Bing response, especially when it doesn't respond anything.
- Add domain models like [Jarvis/HuggingGPT](https://github.com/microsoft/JARVIS/blob/main/CITATION.cff) when performing specific tasks like text summarization.


## Thanks

- [Auto-GPT](https://github.com/Torantulino/Auto-GPT)
- [EdgeGPT](https://github.com/acheong08/EdgeGPT)
