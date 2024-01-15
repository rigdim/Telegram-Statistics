
# Telegram statistic

Python scripts to get statistics based on ***Telegram chat history export***.

It takes (`.json`) file and parse it into tabular format (`.xlsx`) with additional information.

## Overview

By using this script you can get two `.xlsx` that have next data from your chat exported messages:

### First book

- List of users who wrote something and other user that a users who are in the chat but haven’t written anything.
- List of deleted accounts and users who left the chat, whose messages remained in history.
- Activity for each user in the last 14, 30, 90 days with visualization.
- Messages count.
- Region that users mentioned in their messages.

### Second book

- Mentions of various incidents in all regions over the entire period of time with visualization.
- Comparement with actual system failures messages (from telegram bot).

## How to use it

Move to script directory using `cd`.

Create venv & install requirements:

#### Windows

```bash
python -m venv venv

venv\Sripts\activate

pip install -r requirements.txt
```

#### Linux

```bash
python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### Export messages

Using Telegram's Desktop or Web interfaces, go to the chat you want to parse, click on the options button (three dots in the upper right corner) and them click on ***Export chat history***.

In the dialog window, right next to ***Format***, choose `.json`.

![Chat export](https://dl.dropbox.com/scl/fi/3li1hd5sldafiy7rtjjce/export_telegram.png?rlkey=to66ro2ios4jsy3oz0g1d6qu9&dl=0)

After the backup is completed, Telegram will generate a `results.json` file. Next you need to copy or move it to `./docs` folder in script directory.

### Export members (Optional)

*Do it to find who wrote something and then leave chat.*

1. Copy javascipt code from `copy_members.js` 
2. Insert it in ***DevTools console***
3. Copy output and put it `members.json` file in `docs` folder (create file if it doesn't exist).
<details> <summary>Javascript code</summary>

```javascript
function getTextFromElement(element) {
    let text = '';

    if (element.nodeType === 3) {
        text += element.nodeValue.trim().replace(/"/g, "'");
    }
    if (element.nodeType === 1 && element.tagName.toLowerCase() === 'img') {
        const altText = element.alt || '';
        text += altText.trim().replace(/"/g, "'");
    }
    if (element.childNodes.length > 0) {
        for (let i = 0; i < element.childNodes.length; i++) {
            text += getTextFromElement(element.childNodes[i]);
        }
    }
    return text;
}

userList = [];

document.body.querySelectorAll('.chatlist-chat.chatlist-chat-abitbigger>div>div>span.peer-title').forEach((peer) =>
{
    tuple = '{"id": "' + String(peer.dataset.peerId) + '", "name": "' + String(getTextFromElement(peer)) + '"}';
    userList.push(tuple);
})
console.log("[" + userList.join(",\n") + "]");
```

</details>

### Run script


Run the script using `.bat` file. 

Two `.xlsx` files will be created in `./docs` folder.