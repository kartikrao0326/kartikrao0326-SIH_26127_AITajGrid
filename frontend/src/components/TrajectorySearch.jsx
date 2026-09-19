import React, { useState } from 'react';

const TrajectorySearch = ({ user, onSearch }) => {
  const [plate, setPlate] = useState('');
  const [reason, setReason] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!reason.trim()) {
      alert("Reason/case reference is required.");
      return;
    }
    
    try {
      const res = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plate, reason, user: user.username })
      });
      
      if (!res.ok) {
        const error = await res.json();
        alert(error.detail || "Search failed");
        return;
      }
      
      const data = await res.json();
      onSearch(data);
    } catch (err) {
      console.error(err);
      alert("Error searching trajectory");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Target Plate Number</label>
        <input 
          className="w-full px-4 py-2.5 bg-slate-950/50 border border-slate-700 rounded-lg text-sm text-slate-100 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-mono" 
          placeholder="e.g. DL-4C-1234" 
          value={plate} 
          onChange={e => setPlate(e.target.value)} 
          required 
        />
      </div>
      <div className="space-y-2">
        <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Audit Case Reference</label>
        <input 
          className="w-full px-4 py-2.5 bg-slate-950/50 border border-slate-700 rounded-lg text-sm text-slate-100 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all" 
          placeholder="Required by privacy policy" 
          value={reason} 
          onChange={e => setReason(e.target.value)} 
          required 
        />
      </div>
      <button className="w-full bg-blue-600/20 text-blue-400 border border-blue-500/30 hover:bg-blue-600/30 py-2.5 rounded-lg text-sm font-bold tracking-wide transition-colors" type="submit">
        QUERY DATABASE
      </button>
    </form>
  );
};

export default TrajectorySearch;
