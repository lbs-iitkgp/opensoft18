import openSocket from 'socket.io-client';
const socket = openSocket('http://localhost:8080');

function subscribeToStatusChange(cb) {
    socket.on('statusChange', status => cb(null, status));
  }
  
export { subscribeToStatusChange };