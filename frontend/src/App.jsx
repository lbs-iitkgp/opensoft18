import React, { Component } from 'react';
import axios from 'axios';
import Dropzone from 'react-dropzone';
import DisplacyEnt from './js/displacy-ent';
// import Samples from './components/samples';
import Lexigram from './components/lexigram';
import Dosage from './components/dosage';
import Corenlp from './components/corenlp';
import './styles/App.css';
import './styles/buttons.css';
import './styles/dropzone.css';
import './styles/displacy.css';
import './styles/flexboxgrid/flexboxgrid.min.css';
import { subscribeToStatusChange } from './Socket';
import banner from './banner.png';

class App extends Component {
  constructor() {
    super();
    this.state = {
      preview: null,
      outputObjects: [],
      image_name: '',
      canDownload: false,
      lexigramData: null,
      dosageData: null,
      isFresh: false,
      allText: null,
      status: null,
      nlpData: null,
    };

    subscribeToStatusChange((err, newstatus) => this.setState({
      status: newstatus,
    }));

    this.onDrop = this.onDrop.bind(this);
    this.resetImage = this.resetImage.bind(this);
    this.doDownload = this.doDownload.bind(this);
    this.flipFresh = this.flipFresh.bind(this);
    this.renderSpacy = this.renderSpacy.bind(this);
  }

  onDrop(acceptedFiles) {
    const uploaders = acceptedFiles.map((uploadedFile) => {
      this.setState({
        preview: uploadedFile.preview,
        status: 'Started',
      });
      const formData = new FormData();
      formData.append('image', uploadedFile);
      return axios({
        method: 'post',
        url: 'http://localhost:8080/upload',
        data: formData,
        headers: { 'content-type': 'multipart/form-data' },
      }).then((response) => {
        console.log(response);
        const { data } = response;
        console.log(data);
        this.setState({
          outputObjects: [...this.state.outputObjects, data.image],
          image_name: data.image_name,
          allText: data.all_text,
        });
        this.renderSpacy();
        return axios({
          method: 'get',
          url: `http://localhost:8080/continue/${data.image_name}`,
        });
      }).then((response) => {
        const { data } = response;
        console.log(data);
        this.setState({
          outputObjects: [...this.state.outputObjects, data.replaced_image, data.fresh_image],
          lexigramData: data.lexigram_data,
          dosageData: data.dosage_data,
          isFresh: false,
        });
        return axios({
          method: 'get',
          url: `http://localhost:8080/finish/${data.image_name}`,
        });
      }).then((response) => {
        const { data } = response;
        console.log(data);
        this.setState({
          canDownload: true,
        });
        return axios({
          method: 'get',
          url: `http://localhost:8080/donlp/${data.image_name}`,
        });
      }).then((response) => {
        const { data } = response;
        console.log(data);
        this.setState({
          nlpData: data.nlp_result,
        });
      });
    });

    axios.all(uploaders).then(() => {
      console.log('Image uploaded');
    });
  }

  doDownload(index) {
    return axios({
      method: 'get',
      url: `http://localhost:8080/download/${this.state.image_name}/${index}`,
      responseType: 'blob',
    }).then((response) => {
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      if (index === 0 || index === 2) {
        link.setAttribute('download', `${this.state.image_name}`);
      } else {
        let filename = this.state.image_name;
        filename = filename.substring(0, filename.lastIndexOf('.'));
        link.setAttribute('download', `${filename}.pdf`);
      }
      document.body.appendChild(link);
      link.click();
    });
  }

  resetImage() {
    this.setState({
      preview: null,
      outputObjects: [],
      image_name: '',
      canDownload: false,
      lexigramData: null,
      dosageData: null,
      isFresh: false,
      allText: null,
      status: null,
      nlpData: null,
    });
  }

  flipFresh() {
    this.setState({
      isFresh: !this.state.isFresh,
    });
  }

  renderSpacy() {
    const displacy = new DisplacyEnt('http://localhost:8080', {
      container: '#displacy',
    });

    const ents = ['person', 'org', 'gpe', 'loc', 'product'];
    displacy.render(this.state.allText.text, this.state.allText.ents, ents);
  }

  render() {
    const { lexigramData } = this.state;
    const { dosageData } = this.state;
    const { nlpData } = this.state;
    return (
      <div className="App">
        <div className="App-welcome">
          <div className="team-name">
            Team 3
          </div>
          <div className="welcome-text">
            <img src={banner} alt="DigiCon Banner Image" width="400" height="200" />
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
                <img src={banner} alt="DigiCon Banner Image" class="white-banner" width="150" height="75" />
              </div>
              {
                (this.state.status != null && this.state.status !== 'Complete') ? (
                  <div className="status-message">
                    <div className="message-text">{this.state.status}</div>
                  </div>
                ) : ''
              }
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
                {
                  this.state.outputObjects[0] != null ? (
                    <div className="bboxes-preview col-xs-4">
                      <img src={`data:image/jpeg;base64,${this.state.outputObjects[0]}`} alt="Bounding boxes preview" />
                    </div>
                  ) : (
                    <div className="bboxes-preview col-xs-4">
                      <img src={this.state.preview} alt="Bounding boxes preview" />
                    </div>
                  )
                }
                {
                  this.state.outputObjects[1] != null ? (
                    <div
                      className="bboxes-preview col-xs-4 final-preview"
                      onClick={() => this.flipFresh()}
                      onKeyPress={() => this.flipFresh()}
                      role="button"
                      tabIndex={0}
                    >
                      {
                        this.state.isFresh ? (
                          <img src={`data:image/jpeg;base64,${this.state.outputObjects[1]}`} alt="Bounding boxes preview" />
                        ) : (
                          <img src={`data:image/jpeg;base64,${this.state.outputObjects[2]}`} alt="Bounding boxes preview" />
                        )
                      }
                    </div>
                  ) : (
                    <div className="bboxes-preview col-xs-4">
                      <img src={this.state.preview} alt="Bounding boxes preview" />
                    </div>
                  )
                }
              </div>
            }
            {
              this.state.allText &&
              <div className="row spacy-out">
                <div className="spacy-header">
                  (Direct) Named Entities detected
                </div>
                <div className="col-xs-12 spacy-content" id="displacy" />
              </div>
            }
            {
              this.state.canDownload &&
              <div className="row download-buttons">
                <div className="col-md-3 col-xs-6">
                  <div
                    className="download-button"
                    onClick={() => this.doDownload(0)}
                    onKeyPress={() => this.doDownload(0)}
                    role="button"
                    tabIndex={0}
                  >
                    Download overlaid image
                  </div>
                </div>
                <div className="col-md-3 col-xs-6">
                  <div
                    className="download-button"
                    onClick={() => this.doDownload(1)}
                    onKeyPress={() => this.doDownload(1)}
                    role="button"
                    tabIndex={0}
                  >
                    Download overlaid PDF
                  </div>
                </div>
                <div className="col-md-3 col-xs-6">
                  <div
                    className="download-button"
                    onClick={() => this.doDownload(2)}
                    onKeyPress={() => this.doDownload(2)}
                    role="button"
                    tabIndex={0}
                  >
                    Download clean image
                  </div>
                </div>
                <div className="col-md-3 col-xs-6">
                  <div
                    className="download-button"
                    onClick={() => this.doDownload(3)}
                    onKeyPress={() => this.doDownload(3)}
                    role="button"
                    tabIndex={0}
                  >
                    Download clean PDF
                  </div>
                </div>
              </div>
            }
            <div className="row upper-tables">
              <div className="col-xs-12 col-md-6 lexigram-table">
                {
                  lexigramData &&
                  <div className="lexigram-div">
                    <div className="lexigram-title">
                      Medical knowledge
                    </div>
                    <Lexigram
                      lexigramData={lexigramData}
                    />
                  </div>
                }
              </div>
              <div className="col-xs-12 col-md-6 dosage-table">
                {
                  dosageData &&
                  <div className="dosage-div">
                    <div className="dosage-title">
                      Prescribed dosage information
                    </div>
                    <Dosage
                      dosageData={dosageData}
                    />
                  </div>
                }
              </div>
            </div>
            <div className="row lower-tables">
              <div className="col-xs-12 nlp-table">
                {
                  nlpData &&
                  <div className="nlp-div">
                    <div className="nlp-title">
                      Key entities detected
                    </div>
                    <Corenlp
                      nlpData={nlpData}
                    />
                  </div>
                }
              </div>
            </div>
          </div>
        </header>
      </div>
    );
  }
}

export default App;
