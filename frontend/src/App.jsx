import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ShieldAlert, Map as MapIcon, Search, Activity, PlayCircle, LogOut, Lock, User, Terminal } from 'lucide-react';
import TrajMap from './components/Map';
import TrajectorySearch from './components/TrajectorySearch';
import Analytics from './components/Analytics';
import AlertsPanel from './components/Alerts';

// --- Polished Login Component ---
const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = (e) => {
    e.preventDefault();
    if (username === 'operator' && password === 'operator123') {
      onLogin({ username, role: 'Operator' });
    } else if (username === 'admin' && password === 'admin123') {
      onLogin({ username, role: 'Admin' });
    } else {
      alert('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px]"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px]"></div>
      
      <form onSubmit={handleLogin} className="relative z-10 bg-slate-900/80 backdrop-blur-xl border border-slate-700/50 p-10 rounded-2xl shadow-2xl w-full max-w-md">
        <div className="flex justify-center mb-6">
          <div className="p-4 bg-blue-500/10 rounded-full border border-blue-500/20">
            <Terminal className="w-10 h-10 text-blue-400" />
          </div>
        </div>
        <h2 className="text-3xl mb-2 font-extrabold text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
          TrajGrid OS
        </h2>
        <p className="text-center text-slate-400 mb-8 text-sm">Automated ANPR Surveillance System</p>
        
        <div className="space-y-5">
          <div className="relative">
            <User className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
            <input 
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950/50 border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-slate-500" 
              placeholder="Operator ID" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
            />
          </div>
          <div className="relative">
            <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
            <input 
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-950/50 border border-slate-700 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-slate-500" 
              type="password" 
              placeholder="Passcode" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
            />
          </div>
          <button className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 py-3 rounded-xl font-bold tracking-wide shadow-lg shadow-blue-900/20 transition-all transform hover:scale-[1.02]" type="submit">
            INITIALIZE UPLINK
          </button>
        </div>
      </form>
    </div>
  );
};

// --- Polished Layout ---
const DashboardLayout = ({ user, onLogout, children }) => (
  <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans selection:bg-blue-500/30 relative">
    {/* Futuristic Grid Background */}
    <div className="fixed inset-0 z-0 bg-[linear-gradient(to_right,#1e293b80_1px,transparent_1px),linear-gradient(to_bottom,#1e293b80_1px,transparent_1px)] bg-[size:40px_40px] opacity-20 pointer-events-none"></div>
    <div className="fixed inset-0 z-0 bg-[radial-gradient(circle_800px_at_50%_-30%,#1e3a8a30,transparent)] pointer-events-none"></div>

    <header className="relative z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 px-6 py-4 flex justify-between items-center shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/30">
          <Terminal className="w-6 h-6 text-blue-400" />
        </div>
        <div>
          <h1 className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">
            TRAJGRID
          </h1>
          <div className="text-[10px] uppercase font-mono tracking-[0.2em] text-slate-400 -mt-1">Surveillance OS</div>
        </div>
        <span className="ml-4 font-mono text-[10px] font-bold border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-md flex items-center space-x-1">
          <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
          <span>{user.role} AUTHENTICATED</span>
        </span>
      </div>
      <div className="flex items-center space-x-4">
        <button 
          onClick={() => fetch('http://localhost:8000/api/seed', {method:'POST'})} 
          className="group relative flex items-center space-x-2 bg-blue-600/10 text-blue-400 border border-blue-500/30 hover:bg-blue-600 hover:text-white hover:border-blue-500 px-5 py-2.5 rounded-lg text-xs font-bold tracking-widest transition-all overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <PlayCircle className="w-4 h-4 relative z-10" />
          <span className="relative z-10">INITIATE SENSORS</span>
        </button>
        <button 
          onClick={onLogout} 
          className="flex items-center space-x-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 px-3 py-2.5 rounded-lg text-sm font-semibold transition-all border border-transparent hover:border-red-500/20"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
    <main className="relative z-10 flex-1 p-6 max-w-[1800px] mx-auto w-full">
      {children}
    </main>
  </div>
);

// --- App Root ---
const App = () => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('trajgrid_user');
    return saved ? JSON.parse(saved) : null;
  });
  
  const [liveEvent, setLiveEvent] = useState(null);
  const [searchedTrajectory, setSearchedTrajectory] = useState(null);

  useEffect(() => {
    if (!user) return;
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'plate_event') setLiveEvent(data.data);
    };
    return () => ws.close();
  }, [user]);

  if (!user) return <Login onLogin={userData => { setUser(userData); localStorage.setItem('trajgrid_user', JSON.stringify(userData)); }} />;

  return (
    <BrowserRouter>
      <DashboardLayout user={user} onLogout={() => { setUser(null); localStorage.removeItem('trajgrid_user'); }}>
        <Routes>
          <Route path="/" element={
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              
              {/* Left Column: Map & Analytics (Spans 8 columns) */}
              <div className="lg:col-span-8 flex flex-col space-y-6">
                
                {/* Map Card */}
                <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.5)] ring-1 ring-white/5 flex flex-col">
                  <div className="px-5 py-3 border-b border-slate-700/50 flex items-center justify-between bg-gradient-to-r from-slate-800/80 to-transparent">
                    <div className="flex items-center space-x-3">
                      <MapIcon className="w-5 h-5 text-blue-400" />
                      <h2 className="font-bold text-slate-100 tracking-widest text-sm uppercase">Live Tactical Grid</h2>
                    </div>
                    {liveEvent ? (
                      <span className="flex items-center space-x-2 text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                        </span>
                        <span>INTERCEPT: {liveEvent.plate}</span>
                      </span>
                    ) : (
                      <span className="text-xs font-mono text-slate-500 uppercase tracking-widest">Awaiting Data...</span>
                    )}
                  </div>
                  <div className="p-1.5 bg-slate-950/80">
                    <div className="rounded-xl overflow-hidden border border-slate-800 shadow-inner">
                      <TrajMap liveEvent={liveEvent} searchedTrajectory={searchedTrajectory} onClear={() => setSearchedTrajectory(null)} />
                    </div>
                  </div>
                </div>

                {/* Analytics Wrapper */}
                <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.5)] ring-1 ring-white/5 p-6 relative overflow-hidden flex-1">
                   <div className="absolute top-0 right-0 p-6 opacity-[0.03] transform translate-x-4 -translate-y-4">
                     <Activity className="w-64 h-64" />
                   </div>
                   <Analytics />
                </div>
              </div>
              
              {/* Right Column: Search & Alerts (Spans 4 columns) */}
              <div className="lg:col-span-4 flex flex-col space-y-6">
                
                {/* Search Card */}
                <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.5)] ring-1 ring-white/5 overflow-hidden">
                  <div className="px-5 py-3 border-b border-slate-700/50 flex items-center justify-between bg-gradient-to-r from-slate-800/80 to-transparent">
                    <div className="flex items-center space-x-3">
                      <Search className="w-5 h-5 text-indigo-400" />
                      <h2 className="font-bold text-slate-100 tracking-widest text-sm uppercase">Trajectory Query</h2>
                    </div>
                  </div>
                  <div className="p-6 bg-slate-950/20">
                    <TrajectorySearch user={user} onSearch={setSearchedTrajectory} />
                  </div>
                </div>

                {/* Alerts Card */}
                <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700/50 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.5)] ring-1 ring-white/5 overflow-hidden flex flex-col flex-1" style={{minHeight: '400px'}}>
                  <div className="px-5 py-3 border-b border-red-900/30 flex items-center justify-between bg-gradient-to-r from-red-950/40 to-transparent sticky top-0 z-10">
                    <div className="flex items-center space-x-3">
                      <ShieldAlert className="w-5 h-5 text-red-500" />
                      <h2 className="font-bold text-slate-100 tracking-widest text-sm uppercase">Watchlist Alerts</h2>
                    </div>
                  </div>
                  <div className="p-5 flex-1 overflow-y-auto custom-scrollbar bg-slate-950/20">
                    <AlertsPanel user={user} />
                  </div>
                </div>

              </div>
            </div>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </DashboardLayout>
    </BrowserRouter>
  );
};

export default App;
