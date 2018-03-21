import React, { Component } from 'react';
import Samples from './components/samples';
import './App.css';
import SimpleReactFileUpload from './fileUpload'

class App extends Component {
  render() {
    var headerStyle={
      fontSize:60,
      color: "blue",
    }

    return (
      <div className="App">
        <header className="App-header">
          <h1 style={headerStyle} className="App-title">Welcome to DigiCon</h1>
          <Samples />
          <SimpleReactFileUpload />
        </header>
      </div>
    );
  }
}

export default App;
