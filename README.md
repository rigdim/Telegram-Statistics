
# Telegram statistic

Python scripts to get statistics based on Telegram chat messages export.

It takes (`JSON`) file and parse it into tabular format (`xlsx`) with additional information.

## How to use it

Create venv & install requirements:

### Windows

```bash
python -m venv venv

venv/Source/activate

pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

Using Telegram's Desktop or Web interfaces, go to the chat you want to parse, click on the options button (three dots in the upper right corner) and them click on `Export chat history`. In the dialog window, right next to `Format`, chose `JSON`. After the backup is completed, Telegram will generate a `results.json` file.
Next you need to copy or move it to script directory and optionally rename it.

Command to run the script:

```bash
python telegram-chat-parser.py <jsonfile.json>
```

For chat backup in `results.json`, a `.xlsx` file will be created in the same directory.
