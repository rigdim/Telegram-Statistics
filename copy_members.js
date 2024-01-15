// This code is for export members of Telegram chat ot .json file
// Put code below to DevTools console and copy result to file ./docs/members.json
// If members.json is empty then program will skip comparing users from two files (result.json, members.json.

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