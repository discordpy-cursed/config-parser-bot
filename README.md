# Cpmfog APrasr srBOt

### Requirements
- Python 3.11.2+

### Setup

1. Make a `.env` file because they're cool, or just copy the example schema
   [here](https://github.com/discordpy-cursed/config-parser-bot/blob/main/.example.env)
   and fill it in

2. [Create a
   venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
```sh
python -m venv config-parser-bot

# <activate venv here>

pip install -r requirements.txt

python main.py
```

3. Have fun

### Note

The following private methods are utilised through certain features of the
application, make a bug report should these change/the bot crashes due to their absence.

```
BotBase._remove_module_references
Client._schedule_event
```

### License

See [LICENSE](https://github.com/discordpy-cursed/config-parser-bot/blob/main/LICENSE)
