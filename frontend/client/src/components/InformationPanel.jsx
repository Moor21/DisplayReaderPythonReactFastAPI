import {useState, useEffect} from 'react';
import "../styles/InformationPanel.css";
function InformationPanel({ displayStatus, numbersFromDisplay }) {
  const [blurValue, setBlurValue] = useState(null);
  const [morphValue, setMorphValue] = useState(null);
  return (
    <div className="information-panel">
      <div className="display-status-box">
       <p className="box-title">Reading Status</p>
       <div className="rows">
        <div className="display-status-subbox">
            <span className="status-title">Display Status</span>
            <span className="status-main-text">{displayStatus ? "Found" : "Not found"}</span>
            <span className="status-footer-text">Searching for display...</span>
       </div>
       <div className="display-status-subbox">
            <span className="status-title">Numbers</span>
            <span className="status-main-text">{numbersFromDisplay ? numbersFromDisplay : "None"}</span>
            <span className="status-footer-text">{!numbersFromDisplay && "No digits detected"}</span>
       </div>
       </div>
      </div>
      <div className="conf-menu">
        <div>
          <p className="box-title">Configurations</p>
        </div>
        <div className="form">
          <div>
            <label className='main_thresh_label' htmlFor="thresholds">Threshold</label>
            <label className='small_thresh_label' htmlFor=""> Min <input type="range" name="" id="" /> <input className='num_inp' type="number" name="" id="" /></label>
            <label className='small_thresh_label' htmlFor=""> Max <input type="range" name="" id="" /> <input className='num_inp' type="number" name="" id="" /></label>
          </div>
          <div>
            <label className='kernel_labels' htmlFor="blur">Blur_kernel size </label> 
            <select onChange={(e)=>setBlurValue(e.target.value)} name="" id="">
                <option value="3">3x3</option>
                <option value="5">5x5</option>
                <option value="7">7x7</option>
                <option value="9">9x9</option>
                <option value="12">12x12</option>
            </select>
           

            <label className='kernel_labels' htmlFor="blur">Morph_kernel size</label> 
            <select onChange={(e)=>setMorphValue(e.target.value)} name="" id="">
                <option value="3">3x3</option>
                <option value="5">5x5</option>
                <option value="7">7x7</option>
                <option value="9">9x9</option>
                <option value="12">12x12</option>
            </select> 

            
          </div>
          <div>
            <label className='main_thresh_label' htmlFor="factors">Display border crop</label>
            <label className='small_thresh_label' htmlFor=""></label>
            <input className='num_inp' placeholder="fx..." type="number" name="factors" id="" />
            <input className='num_inp' placeholder="fy..." type="number" name="factors" id="" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default InformationPanel;
