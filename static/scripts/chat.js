const socket = io();
function sendMessage() {
    var input = document.querySelector("#msginput");
    if(openedchat != ""){
        socket.emit("send", {'text': input.value, 'chatid': openedchat});
        input.value = "";
    };
};
var chats = [];
var chatids = [];
var openedchat = '';
var ownname = '';
function addMessage(name, text) {
    var div = document.createElement("div");
    div.setAttribute('class', 'message');
    var title = document.createElement("h1");
    title.innerHTML = name
    var description = document.createElement('p');
    description.innerHTML = text;
    div.appendChild(title);
    div.appendChild(description);
    if(name == ownname){div.setAttribute("owner", "")};
    var msgs = document.querySelector("#messages");
    msgs.appendChild(div); 
}
function loadChat(id){
    socket.emit('getchat', {'chatid': id})
};

window.onload = function () {
    const chatlist = document.querySelector('#chatlist');
    const msgs = document.querySelector("#messages");
    const chatbox = document.querySelector("#messages");
    const inp = document.querySelector("#msginput");
    
    socket.on('connect', () => {
        console.log("connected");
        socket.emit('listchats');
    });

    socket.on('yourdata', (data) => {
        ownname = data.name;
    });

    socket.on('error', (data) => {
        if(data['text'] == "AUTHERROR"){
            window.location.href = '/login';
        };
    });

    socket.on('chat', (data) => {
        if(data['chat'] != 'notfound'){
            console.log(data)
            inp.disabled = false;
            openedchat = data.chatid;
            msgs.innerHTML = "";
            chat = data.chat
            if(!chatids.includes(data.chatid)){chatids.push(data.chatid)};
            chats[data.chatid] = data.chat;
            document.querySelector("#chattitle").innerHTML = chat.title;
            document.querySelector("#chatdescr").innerHTML = chat.description;
            messages = chat.messages
            for(message of messages){
                addMessage(message.name, message.text);
            };
            chatbox.scrollTop += msgs.children.length * 500;
        }else{
            alert('notfound error');
        }
    });

    socket.on('message', (data) => {
        if(data['chat'] == openedchat){
            addMessage(data.name, data.text);
            console.log(data);
        }
    })

    socket.on('chats', (data) => {
        chatlist.innerHTML = '';
        chats = data.chats;
        chatids = data.chatids;
        console.log(chats);
        for(chatid of chatids){
            chat = chats[chatid];
            let div = document.createElement("div");
            div.setAttribute('class', 'user');
            var title = document.createElement("h1");
            title.innerHTML = chat.title
            var description = document.createElement('p');
            description.innerHTML = chat.description;
            div.chatid = chatid;
            div.onclick = function() {loadChat(div.chatid);};
            div.appendChild(title);
            div.appendChild(description);
            chatlist.appendChild(div);
        };
    });

};