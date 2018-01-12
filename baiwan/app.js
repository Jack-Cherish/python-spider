var http = require('http');
var fs = require('fs');
var schedule = require("node-schedule"); 
var message = {};
var count = 0;
var server = http.createServer(function (req,res){
    fs.readFile('./index.html',function(error,data){
        res.writeHead(200,{'Content-Type':'text/html'});
        res.end(data,'utf-8');
    });
}).listen(80);
console.log('Server running!');
var lineReader = require('line-reader');
function messageGet(){
    lineReader.eachLine('file.txt', function(line, last) {
        count++;
        var name = 'line' + count;
        console.log(name);
	console.log(line);
        message[name] = line;
    });  
    if(count == 25){
    	count = 0;
    }
    else{
    	for(var i = count+1; i <= 25; i++){
  	    var name = 'line' + i;
            message[name] = 'f';
	}
  	count = 0;
    }
}
var io = require('socket.io').listen(server);
var rule = new schedule.RecurrenceRule();
var times = [];
for(var i=1; i<1800; i++){
    times.push(i);
}
rule.second = times;
schedule.scheduleJob(rule, function(){
        messageGet();
});
io.sockets.on('connection',function(socket){
       // console.log('User connected' + count + 'user(s) present');
        socket.emit('users',message);
        socket.broadcast.emit('users',message);

    socket.on('disconnect',function(){
        console.log('User disconnected');
        //socket.broadcast.emit('users',message);  
    });
});
