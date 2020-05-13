import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = [] # list of channels created
contents = {} # dict of channel (keyword) : Comments
users = [] # list of users online
current_channel = None

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on('access')
def access():        
    emit('list channels',channels, broadcast = False)   
    if current_channel is not None:      
        emit('list contents',current_channel, broadcast = False)
    latest = len(users) - 1    
    if latest >= 0:
        emit('user name', users[latest], broadcast = False)

@socketio.on('get name')
def get_name(data):   
    name = data["name"]
    for user in users:
        if user == name:
            t = "/e/"
            emit('user name',t, broadcast = False)
            return
    users.append(name)  
    emit('user name', name, broadcast = False)



@socketio.on('create channel')
def create(data):
    channel = data["channel"]   
    # prevent creating an existed channel
    for x in channels:
        if x == channel:          
            emit('list channels',channels, broadcast = True)
            return    
    channels.append(channel)
    channel_dict = {channel:[[]]}
    contents.update(channel_dict)
    emit('list channels',channels, broadcast = True)

@socketio.on('get content')
def get_content(data):  
    name = data["name"]      
    content = contents.get(name)  # get content with the key is Name of channel    
    global current_channel          # need to declare global
    current_channel = content       # set to current channel
    emit('list contents', content, broadcast = False)

@socketio.on('comment')
def comment(data):  
    content = data["content"]
    channel_name = data["name"]  

    # get {[name]:[[user,comment]]} 
    cmt_array = content.get(channel_name)
    comment = cmt_array[0]   #get [user,comment]

    channel_list = contents.get(channel_name) # get channel list(array) with key is channel name  
    channel_list.append(comment) #append the array[user,comment] into the channel list  
    emit('add comment', channel_list, broadcast = True)

if __name__ == '__main__':
    socketio.run(app)

