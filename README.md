
# Telegram statistic

Python scripts to get statistics based on Telegram chat messages export.

It takes (`.json`) file and parse it into tabular format (`.xlsx`) with additional information.

## How to use it

Move to script directory using `cd`.

Create venv & install requirements:

### Windows

```bash
python -m venv venv

venv\Sripts\activate

pip install -r requirements.txt
```

### Linux

```bash
python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### Export

Using Telegram's Desktop or Web interfaces, go to the chat you want to parse, click on the options button (three dots in the upper right corner) and them click on ***Export chat history***.

In the dialog window, right next to ***Format***, choose `.json`.

![Chat export](https://dl.dropbox.com/scl/fi/3li1hd5sldafiy7rtjjce/export_telegram.png?rlkey=to66ro2ios4jsy3oz0g1d6qu9&dl=0)

After the backup is completed, Telegram will generate a `results.json` file. Next you need to copy or move it to `./docs` folder in script directory.

### Run script


Run the script using `.bat` file. 

A `.xlsx` file will be created in `./docs` folder.