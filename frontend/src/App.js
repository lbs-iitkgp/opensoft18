import React, { Component } from 'react';
import Samples from './components/samples';
import './App.css';


class App extends Component {
  render() {
    var myStyle={
      fontSize:60,
      color: "blue",
    }

    return (
      <div className="App">
        <header className="App-header">
          <h1 style={myStyle} className="App-title">Welcome to DigiCon</h1>
          <Samples />
        </header>
      </div>
    );
  }
}

export default App;
