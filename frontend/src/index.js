import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import SimpleReactFileUpload from './fileUpload'
import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(<App />, document.getElementById('root'));
ReactDOM.render(<SimpleReactFileUpload />, document.getElementById('root1'));
registerServiceWorker();
