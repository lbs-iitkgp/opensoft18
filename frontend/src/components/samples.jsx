import React from 'react';
import '../styles/samples.css';

// Import sample images
import Sample1 from '../samples/1.jpg';
import Sample2 from '../samples/2.jpg';
import Sample3 from '../samples/3.jpg';
import Sample4 from '../samples/4.jpg';
import Sample5 from '../samples/5.jpg';

const Samples = () => (
  <div className="samplesContainer">
    <div className="sampleImage">
      <img src={Sample1} alt="Sample 1" />
    </div>
    <div className="sampleImage">
      <img src={Sample2} alt="Sample 2" />
    </div>
    <div className="sampleImage">
      <img src={Sample3} alt="Sample 3" />
    </div>
    <div className="sampleImage">
      <img src={Sample4} alt="Sample 4" />
    </div>
    <div className="sampleImage">
      <img src={Sample5} alt="Sample 5" />
    </div>
  </div>
);

export default Samples;
