# Cpmfog APrasr srBOt

1. Make a `.env` file because they're cool, example schema [here](https://github.com/discordpy-cursed/config-parser-bot/blob/main/.example.env)

```bash
PREFIX="?"
TOKEN="token"
```

2. [Create a venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
3. Run this

```bash
pip install -r requirements.txt
python main.py
```

4. Have fun

### Note

The following private methods are utilised through certain features of the application, make a bug report should these change.

```
BotBase._remove_module_references
Client._schedule_event
```

### License

See [LICENSE](https://github.com/discordpy-cursed/config-parser-bot/blob/main/LICENSE)
