import React, { Component } from 'react';
import axios from 'axios';
import Dropzone from 'react-dropzone';
import Samples from './components/samples';
import './App.css';
import SimpleReactFileUpload from './fileUpload';

class App extends Component {
  constructor() {
    super();
    this.state = { preview: null };

    this.onDrop = this.onDrop.bind(this);
  }

  onDrop(acceptedFiles) {
    const uploaders = acceptedFiles.map((uploadedFile) => {
      this.setState({
        preview: uploadedFile.preview,
      });
      const formData = new FormData();
      formData.append('image', uploadedFile);
      return axios.post('http://localhost:8080/upload', formData, {
        headers: { 'content-type': 'multipart/form-data' },
      }).then((response) => {
        const { data } = response;
        console.log(data);
      });
    });

    axios.all(uploaders).then(() => {
      console.log('Image uploaded');
    });
  }

  render() {
    return (
      <div className="App">
        <div className="App-welcome">
          <div className="welcome-text">
            DigiCon
            <div className="App-description">
              { 'It is hard to change a doctor\'s handwriting. But it shouldn\'t be hard to read them.' }
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
          <Dropzone
            onDrop={this.onDrop}
            accept="image/*"
            multiple={false}
          >
            <p>Try dropping some files here, or click to select files to upload.</p>
          </Dropzone>
          {
            this.state.preview && <img src={this.state.preview} alt="Uploaded preview" />
          }
        </header>
      </div>
    );
  }
}

export default App;
