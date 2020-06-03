
document.addEventListener('DOMContentLoaded', () => {  
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.emit('access');  
    let global_name = localStorage.getItem("name");
    let current_channel;
    createname();

    function createname(){
        const temp = document.createElement('h6');
        temp.innerHTML = global_name;
        document.querySelector('#profile-tray').append(temp);   
    }
 
    //1 create channel - send event to server
    socket.on('connect',() =>{                   
        document.querySelector('#create_channel').onsubmit = () =>{         
            const channel = document.querySelector('#channel_name').value;          
            document.querySelector('#channel_name').value = "";
            socket.emit('create channel',{'channel': channel});         
            return false;           
        }        
    });
    

    //2 get list of channels from server
    socket.on('list channels', data => {             
        //clear the view of previous list
        let temp = document.querySelectorAll('.channelnode');
        if(temp !== null){
            temp.forEach(function (e){
                e.parentNode.removeChild(e);
            });
        }
        // create the new one
        for (var i = 0; i < data.length; i++) {
            createChannel(data[i]);          
        }              
    });

    //function to add channel to channels, and attach event listener to each channel
    function createChannel(name){                
        const li = document.createElement('li');
        li.className = 'channelnode';
        li.addEventListener('click',openChannel); // addEventListener cant pass func(var)
        li.innerHTML = name;                     
        document.querySelector('#channels').append(li);
    }

    //get content of a channel from server to view
    function openChannel(){           
        let name = this.innerHTML; // name of the Channel
        current_channel = name;
        socket.emit('get content',{'name':name});
        comment(name);       
    }

    //listen to comment
    function comment(name){         
        document.querySelector('#add_comment').onsubmit = () => {          
            let comment = document.querySelector('#comment').value;   
            time = new Date(); // Add timestamp
            comment = "(" + time.getHours() + ":" + time.getMinutes() + "-" + time.getDate() + "/" + time.getMonth() + ") " + comment;
            document.querySelector('#comment').value = "";                
            const user = global_name;
            let content = {[name]:[[user,comment]]};  
            socket.emit('comment',{'content':content, 'name':name});       
            return false;
        }
    }
   
    //3 get content of a channel from server
    socket.on('list contents', data => {              
        //clear the view of previous list of comments
        let temp = document.querySelectorAll('.commentnode');
        if(temp !== null){
            temp.forEach(function (e){
                e.parentNode.removeChild(e);
            });
        }      
        data.forEach(function(comment){ //comment is an array containing [user,comment]
            if(comment.length !== 0){
                user_name = comment[0];
                user_comment = comment[1];
                createComments(user_name, user_comment);
            }
        });
    });

    // Add comment
    socket.on('add comment', data => {
        content_of_channel = data.content;
        channel_name = data.channel_name;
        l = content_of_channel.length - 1;
        if(channel_name == current_channel){
            createComments(content_of_channel[l][0], content_of_channel[l][1]);
        }
    });

    //function to add comments to view
    function createComments(user,comment){       
        const argument = document.createElement('p');
        argument.className = 'commentnode';        
        argument.innerHTML = user + ": " + comment;
        document.querySelector('#view').append(argument);      
    }  
   
});

