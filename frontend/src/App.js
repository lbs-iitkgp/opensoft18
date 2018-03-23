import React from 'react';
import Samples from './components/samples';
import './App.css';
import SimpleReactFileUpload from './fileUpload';

const App = () => (
  <div className="App">
    <div className="App-welcome">
      <div className="welcome-text">
        DigiCon
        <div className="App-description">
          It is hard to change a doctor's handwriting. But it shouldn't be hard to read them.
        </div>
      </div>
      <div className="welcome-bottom" />
    </div>
    <header className="App-main">
      <h1 className="App-title">
        Welcome to DigiCon
      </h1>
      <Samples />
      <SimpleReactFileUpload />
    </header>
  </div>
);

export default App;
