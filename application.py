import os

from flask import Flask, render_template, request, jsonify, redirect,url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

channels = [] # list of channels created
contents = {} # dict of channel (keyword) : Comments
current_channel = None
test_user = None

@app.route("/")
def index():  
    return render_template("access.html")

@app.route("/home")
def home():
    print('inside home')
    return render_template("index.html")    


@socketio.on('access')
def access():        
    emit('list channels',channels, broadcast = False)   
    if current_channel is not None:      
        emit('list contents',current_channel, broadcast = False)

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

    content_of_channel = contents.get(channel_name) # get channel list(array) with key is channel name  
    content_of_channel.append(comment) #append the array[user,comment] into the channel list  
    emit('add comment', {'content':content_of_channel,'channel_name':channel_name}, broadcast = True)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
    socketio.run(app)
