import React, { Component } from 'react';
import Samples from './components/samples';
import './App.css';

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h1 className="App-title">Welcome to DigiCon</h1>
          <Samples />
        </header>
      </div>
    );
  }
}

export default App;
