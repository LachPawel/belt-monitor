import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Activity, 
  Settings, 
  Upload, 
  FileText, 
  AlertCircle, 
  CheckCircle2,
  Clock,
  MoreHorizontal,
  Play,
  Download,
  FileSpreadsheet,
  FileJson
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_URL = '/api/v1';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isUploading, setIsUploading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);
    setAnalysisResult(null);

    const formData = new FormData();
    formData.append('file', file);
    // Default params
    const params = new URLSearchParams({
      min_width_threshold: '100',
      max_width_threshold: '2000',
      seam_threshold: '0.3',
      sample_rate: '1'
    });

    try {
      const response = await fetch(`${API_URL}/analyze?${params}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analiza nie powiodła się');
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background text-primary font-sans selection:bg-accent selection:text-white">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-surface/50 flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
            <Activity className="w-5 h-5 text-black" />
          </div>
          <span className="font-bold text-lg tracking-tight">BeltMonitor AI</span>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4">
          <NavItem icon={<LayoutDashboard />} label="Panel" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <NavItem icon={<Activity />} label="Analiza" active={activeTab === 'analysis'} onClick={() => setActiveTab('analysis')} />
          <NavItem icon={<FileText />} label="Raporty" active={activeTab === 'reports'} onClick={() => setActiveTab('reports')} />
          <NavItem icon={<Settings />} label="Ustawienia" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
        </nav>

        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-surface border border-border">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-accent to-emerald-300"></div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">Operator</p>
              <p className="text-xs text-secondary truncate">Kierownik Linii A</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-background/80 backdrop-blur-sm sticky top-0 z-10">
          <h1 className="text-xl font-semibold">
            {activeTab === 'dashboard' && 'Przegląd Produkcji'}
            {activeTab === 'analysis' && 'Analiza Taśmy'}
            {activeTab === 'reports' && 'Wygenerowane Raporty'}
            {activeTab === 'settings' && 'Konfiguracja Systemu'}
          </h1>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-2 text-sm text-secondary">
              <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
              System Operacyjny
            </span>
          </div>
        </header>

        <div className="p-8 max-w-7xl mx-auto space-y-8">
          {activeTab === 'dashboard' && <DashboardView />}
          {activeTab === 'analysis' && (
            <AnalysisView 
              isUploading={isUploading} 
              onUpload={handleFileUpload} 
              result={analysisResult}
              error={uploadError}
            />
          )}
          {activeTab === 'reports' && <ReportsView />}
          {activeTab === 'settings' && <SettingsView />}
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
        active 
          ? 'bg-white text-black shadow-lg shadow-white/5' 
          : 'text-secondary hover:text-primary hover:bg-surface'
      }`}
    >
      {React.cloneElement(icon, { size: 18 })}
      {label}
    </button>
  );
}

function DashboardView() {
  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Śr. Szerokość Taśmy" value="498.2 mm" trend="+0.4%" status="good" />
        <StatCard title="Wykryte Szwy" value="1,240" trend="+12%" status="neutral" />
        <StatCard title="Anomalie" value="3" trend="-2" status="good" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-semibold text-lg">Harmonogram Produkcji</h3>
              <p className="text-sm text-secondary">Tydzień 42 • 14 Paź - 20 Paź</p>
            </div>
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-accent"></div>
              <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
              <div className="w-2 h-2 rounded-full bg-red-500"></div>
            </div>
          </div>
          
          {/* Timeline Mock */}
          <div className="space-y-4">
            <div className="flex text-xs text-secondary border-b border-border pb-2">
              <div className="w-24">Zasób</div>
              <div className="flex-1 grid grid-cols-6 gap-2 text-center">
                <span>08:00</span><span>10:00</span><span>12:00</span><span>14:00</span><span>16:00</span><span>18:00</span>
              </div>
            </div>
            
            <TimelineRow 
              resource="Linia A" 
              sub="Wyd: 100%" 
              items={[
                { name: "Zlecenie #4421", status: "W toku", start: 1, span: 3, color: "bg-surface border border-border" }
              ]} 
            />
            <TimelineRow 
              resource="Montaż 1" 
              sub="Wyd: 85%" 
              items={[
                { name: "Zlecenie #4425", status: "Opóźnienie 15m", start: 3, span: 2, color: "bg-surface border border-border text-yellow-500" },
                { name: "Konserwacja", status: "", start: 5, span: 1, color: "bg-surface/50 border border-border/50 text-secondary" }
              ]} 
            />
             <TimelineRow 
              resource="Pakowanie" 
              sub="Wyd: 40%" 
              items={[
                { name: "Zlecenie #4419", status: "Zgodnie z planem", start: 2, span: 2, color: "bg-surface border border-border" }
              ]} 
            />
          </div>

          <div className="mt-6 bg-black rounded-lg p-4 flex items-center gap-3 border border-border">
            <div className="w-6 h-6 rounded-full bg-purple-500/20 flex items-center justify-center">
              <div className="w-2 h-2 rounded-full bg-purple-500"></div>
            </div>
            <p className="text-sm"><span className="font-semibold text-purple-400">Wskazówka AI:</span> Przeniesienie Zlecenia #4425 na Linię B zaoszczędziłoby 45 min.</p>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4">Ostatnie Alerty</h3>
          <div className="space-y-4">
            <AlertItem title="Odchylenie Szerokości" time="10:42" type="warning" />
            <AlertItem title="Wykryto Szew" time="10:30" type="info" />
            <AlertItem title="Start Systemu" time="08:00" type="success" />
          </div>
        </div>
      </div>
    </>
  );
}

function AnalysisView({ isUploading, onUpload, result, error }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-12rem)]">
      <div className="lg:col-span-1 space-y-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="font-semibold text-lg mb-4">Nowa Analiza</h3>
          <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent/50 transition-colors relative">
            <input 
              type="file" 
              onChange={onUpload} 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept="video/*,image/*"
              disabled={isUploading}
            />
            <div className="flex flex-col items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-surface border border-border flex items-center justify-center">
                {isUploading ? <Activity className="animate-spin text-accent" /> : <Upload className="text-secondary" />}
              </div>
              <div>
                <p className="font-medium">Kliknij by wgrać lub przeciągnij plik</p>
                <p className="text-sm text-secondary">MP4, AVI, JPG, PNG</p>
              </div>
            </div>
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm flex items-center gap-2">
              <AlertCircle size={16} />
              {error}
            </div>
          )}
        </div>

        {result && (
          <div className="bg-surface border border-border rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-lg">Podsumowanie Wyników</h3>
            <div className="space-y-3">
              <ResultRow label="Plik" value={result.source_file} />
              <ResultRow label="Czas trwania" value={`${result.total_frames} klatek`} />
              <ResultRow label="Segmenty" value={result.total_segments} />
              <ResultRow label="FPS" value={result.fps} />
            </div>
            <button className="w-full py-2 bg-white text-black font-medium rounded-lg hover:bg-gray-200 transition-colors">
              Pobierz Pełny Raport
            </button>
          </div>
        )}
      </div>

      <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-6 flex flex-col">
        <h3 className="font-semibold text-lg mb-6">Wizualizacja Szerokości</h3>
        {result ? (
          <div className="flex-1 min-h-[300px]">
             <ResponsiveContainer width="100%" height="100%">
                <LineChart data={result.segments.map(s => ({ name: `Seg ${s.segment_id}`, width: s.avg_width_px }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a' }}
                    itemStyle={{ color: '#fafafa' }}
                  />
                  <Line type="monotone" dataKey="width" stroke="#22c55e" strokeWidth={2} dot={{ fill: '#22c55e' }} />
                </LineChart>
             </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center text-secondary border border-dashed border-border rounded-lg bg-background/50">
            <p>Wgraj plik aby zobaczyć dane</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ReportsView() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await fetch(`${API_URL}/results`);
      const data = await response.json();
      setReports(data.analyses || []);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = (id, format) => {
    window.open(`${API_URL}/reports/${id}/${format}`, '_blank');
  };

  if (loading) {
    return (
      <div className="bg-surface border border-border rounded-xl p-6 flex items-center justify-center h-64">
        <Activity className="animate-spin text-accent" />
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="font-semibold text-lg">Dostępne Raporty</h3>
        <button onClick={fetchReports} className="text-sm text-secondary hover:text-primary">
          Odśwież Listę
        </button>
      </div>
      
      {reports.length === 0 ? (
        <div className="text-secondary text-center py-12 border border-dashed border-border rounded-lg">
          Brak wygenerowanych raportów. Uruchom analizę, aby zobaczyć wyniki.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-secondary">
                <th className="pb-3 font-medium">Data</th>
                <th className="pb-3 font-medium">Plik Źródłowy</th>
                <th className="pb-3 font-medium">Segmenty</th>
                <th className="pb-3 font-medium">FPS</th>
                <th className="pb-3 font-medium text-right">Akcje</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {reports.map((report) => (
                <tr key={report.analysis_id} className="group hover:bg-white/5 transition-colors">
                  <td className="py-4 text-secondary">
                    {new Date(report.created_at).toLocaleString('pl-PL')}
                  </td>
                  <td className="py-4 font-medium">{report.source_file}</td>
                  <td className="py-4">{report.total_segments}</td>
                  <td className="py-4">{report.fps.toFixed(1)}</td>
                  <td className="py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={() => downloadReport(report.analysis_id, 'excel')}
                        className="p-2 hover:bg-white/10 rounded-lg text-emerald-400 transition-colors"
                        title="Pobierz Excel"
                      >
                        <FileSpreadsheet size={18} />
                      </button>
                      <button 
                        onClick={() => downloadReport(report.analysis_id, 'csv')}
                        className="p-2 hover:bg-white/10 rounded-lg text-blue-400 transition-colors"
                        title="Pobierz CSV"
                      >
                        <FileText size={18} />
                      </button>
                      <button 
                        onClick={() => downloadReport(report.analysis_id, 'json')}
                        className="p-2 hover:bg-white/10 rounded-lg text-yellow-400 transition-colors"
                        title="Pobierz JSON"
                      >
                        <FileJson size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function SettingsView() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-surface border border-border rounded-xl p-6 space-y-6">
        <h3 className="font-semibold text-lg border-b border-border pb-4">Konfiguracja Analizy</h3>
        
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary">Domyślna Min. Szerokość (px)</label>
            <input type="number" defaultValue="100" className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-accent" />
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary">Domyślna Max. Szerokość (px)</label>
            <input type="number" defaultValue="2000" className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-accent" />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary">Czułość Detekcji Szwów (0.1 - 1.0)</label>
            <div className="flex items-center gap-4">
              <input type="range" min="0.1" max="1.0" step="0.1" defaultValue="0.3" className="flex-1 accent-accent" />
              <span className="text-sm font-mono w-8">0.3</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-xl p-6 space-y-6">
        <h3 className="font-semibold text-lg border-b border-border pb-4">Ustawienia Systemowe</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium text-sm">Automatyczne Raporty</p>
              <p className="text-xs text-secondary">Generuj PDF po każdej analizie</p>
            </div>
            <div className="w-10 h-6 bg-accent rounded-full relative cursor-pointer">
              <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
            </div>
          </div>

          <div className="flex items-center justify-between py-2">
            <div>
              <p className="font-medium text-sm">Powiadomienia Email</p>
              <p className="text-xs text-secondary">Wysyłaj alerty o anomaliach</p>
            </div>
            <div className="w-10 h-6 bg-border rounded-full relative cursor-pointer">
              <div className="absolute left-1 top-1 w-4 h-4 bg-secondary rounded-full"></div>
            </div>
          </div>

          <div className="pt-4 border-t border-border">
            <button className="w-full py-2 bg-white text-black font-medium rounded-lg hover:bg-gray-200 transition-colors">
              Zapisz Ustawienia
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Components
function StatCard({ title, value, trend, status }) {
  const isPositive = trend.startsWith('+');
  const isGood = status === 'good';
  
  return (
    <div className="bg-surface border border-border rounded-xl p-6">
      <p className="text-sm text-secondary mb-2">{title}</p>
      <div className="flex items-end justify-between">
        <h4 className="text-3xl font-bold tracking-tight">{value}</h4>
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
          isGood ? 'bg-emerald-500/10 text-emerald-400' : 'bg-yellow-500/10 text-yellow-400'
        }`}>
          {trend}
        </span>
      </div>
    </div>
  );
}

function TimelineRow({ resource, sub, items }) {
  return (
    <div className="flex items-center py-3 border-b border-border/50 last:border-0">
      <div className="w-24 shrink-0">
        <p className="font-medium text-sm">{resource}</p>
        <p className="text-xs text-secondary">{sub}</p>
      </div>
      <div className="flex-1 grid grid-cols-6 gap-2 h-12 relative">
        {/* Grid lines */}
        {[0,1,2,3,4,5].map(i => (
          <div key={i} className="border-l border-border/30 h-full absolute top-0" style={{ left: `${(i/6)*100}%` }}></div>
        ))}
        
        {items.map((item, i) => (
          <div 
            key={i}
            className={`rounded-md p-2 text-xs font-medium flex flex-col justify-center ${item.color}`}
            style={{ 
              gridColumnStart: item.start, 
              gridColumnEnd: `span ${item.span}` 
            }}
          >
            <div className="flex justify-between items-center">
              <span className="truncate">{item.name}</span>
              <MoreHorizontal size={12} className="text-secondary" />
            </div>
            {item.status && <span className="text-[10px] opacity-80">{item.status}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

function AlertItem({ title, time, type }) {
  const colors = {
    warning: "text-yellow-400 bg-yellow-400/10",
    info: "text-blue-400 bg-blue-400/10",
    success: "text-emerald-400 bg-emerald-400/10"
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 transition-colors">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${colors[type]}`}>
        {type === 'warning' && <AlertCircle size={16} />}
        {type === 'info' && <Activity size={16} />}
        {type === 'success' && <CheckCircle2 size={16} />}
      </div>
      <div className="flex-1">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-secondary">{time}</p>
      </div>
    </div>
  );
}

function ResultRow({ label, value }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-border/50 last:border-0">
      <span className="text-secondary text-sm">{label}</span>
      <span className="font-medium text-sm">{value}</span>
    </div>
  );
}

export default App;
