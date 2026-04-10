import {useState, useEffect} from 'react';
import "../styles/InformationPanel.css";
function InformationPanel({ displayStatus, numbersFromDisplay }) {
  const [blurValue, setBlurValue] = useState(null);
  const [morphValue, setMorphValue] = useState(null);
  const [minThresh, setMinThresh] = useState(80);
  const [maxThresh, setMaxThresh] = useState(110);
  const [xFactor, setXFactor] = useState(0);
  const [yFactor, setYFactor] = useState(0);
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
          <div className='columns'>
            <label className='main_thresh_label' htmlFor="thresholds">Threshold</label>
            <label className='main_thresh_laber' htmlFor="">Blur kernel size</label>
            <label className='main_thresh_laber' htmlFor="">Morph kernel size</label>
            <label className='main_thresh_label' htmlFor="factors">Display border crop</label>
          </div>
          <div className='columns'>            
            <label className='small_thresh_label' htmlFor=""> Min <input type="range" min={0} max={255} step={1} value={minThresh} onChange={(e)=>setMinThresh(Number(e.target.value))} name="" id="" /> <input className='num_inp' value={minThresh} onChange={(e)=>setMinThresh(Number(e.target.value))} type="number" name="" id="" /></label>
            <select onChange={(e)=>setBlurValue(e.target.value)} name="" id="">
                <option value="3">3x3</option>
                <option value="5">5x5</option>
                <option value="7">7x7</option>
                <option value="9">9x9</option>
                <option value="12">12x12</option>
            </select>
            <input className='num_inp' value={xFactor} onChange={(e)=>setXFactor(Number(e.target.value))} min={0} max={2} step={0.1}  placeholder="fx..." type="number" name="factors" id="" />
          </div>
          <div className='columns'>
             <label className='small_thresh_label' htmlFor=""> Max <input type="range" min={0} max={255} step={1} value={maxThresh} onChange={(e)=>setMaxThresh(Number(e.target.value))} name="" id="" /> <input className='num_inp' value={maxThresh} onChange={(e)=>setMaxThresh(Number(e.target.value))} type="number" name="" id="" /></label>
             <select onChange={(e)=>setMorphValue(e.target.value)} name="" id="">
                  <option value="3">3x3</option>
                  <option value="5">5x5</option>
                  <option value="7">7x7</option>
                  <option value="9">9x9</option>
                  <option value="12">12x12</option>
              </select>
              <input className='num_inp' value={yFactor} onChange={(e)=>setYFactor(Number(e.target.value))} min={0} max={2} step={0.1}  placeholder="fy..." type="number" name="factors" id="" />
          </div>
          <button className='btn'>Send</button>
        </div>
      </div>
    </div>
  );
}

export default InformationPanel;
