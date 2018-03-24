import React, { Component } from 'react';
import axios from 'axios';
import Dropzone from 'react-dropzone';
// import Samples from './components/samples';
import './styles/App.css';
import './styles/dropzone.css';
import './styles/flexboxgrid/flexboxgrid.min.css';

class App extends Component {
  constructor() {
    super();
    this.state = { preview: null };

    this.onDrop = this.onDrop.bind(this);
    this.resetImage = this.resetImage.bind(this);
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

  resetImage() {
    this.setState({
      preview: null,
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
          <div className="main-content">
            <div className="row middle-xs app-title-text">
              <div className="App-title col-xs-6">
                DigiCon
              </div>
              {
                this.state.preview &&
                <div
                  className="new-image col-xs-6"
                  onClick={() => this.resetImage()}
                  onKeyPress={() => this.resetImage()}
                  role="button"
                  tabIndex={0}
                >
                  New image
                </div>
              }
            </div>
            {/* <Samples /> */}
            {
              !this.state.preview &&
              <Dropzone
                onDrop={this.onDrop}
                accept="image/*"
                multiple={false}
                className="image-dropzone"
              >
                <p>
                  Try dropping a prescription here, or click to select a prescription to upload.
                </p>
              </Dropzone>
            }
            {
              this.state.preview &&
              <div className="row previews">
                <div className="original-preview col-xs-4">
                  <img src={this.state.preview} alt="Uploaded preview" />
                </div>
                <div className="bboxes-preview col-xs-4">
                  <img src={this.state.preview} alt="Bounding boxes preview" />
                </div>
                <div className="output-preview col-xs-4">
                  <img src={this.state.preview} alt="Output preview" />
                </div>
              </div>
            }
          </div>
        </header>
      </div>
    );
  }
}

export default App;
