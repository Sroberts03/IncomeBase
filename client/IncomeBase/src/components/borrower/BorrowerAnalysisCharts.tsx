import { FiBarChart2 } from 'react-icons/fi';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

interface BorrowerAnalysisChartsProps {
  activeGraphTab: string;
  setActiveGraphTab: (tab: string) => void;
  getGraphData: () => any[];
}

export default function BorrowerAnalysisCharts({
  activeGraphTab,
  setActiveGraphTab,
  getGraphData
}: BorrowerAnalysisChartsProps) {
  return (
    <section className="max-w-4xl mx-auto px-4 mb-8">
      <h2 className="text-lg font-semibold text-gray-700 mb-3">Income Graph</h2>
      <div className="bg-white rounded-xl border border-gray-100 p-6">
        
        {/* Tabs */}
        <div className="flex space-x-4 mb-6">
          {['incomeYtd', 'incomeLast6', 'incomeLast12', 'incomeLast24'].map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 rounded-md transition-colors ${activeGraphTab === tab ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
              onClick={() => setActiveGraphTab(tab)}
            >
              {tab === 'incomeYtd' && 'Year-to-Date'}
              {tab === 'incomeLast6' && 'Last 6 Months'}
              {tab === 'incomeLast12' && 'Last 12 Months'}
              {tab === 'incomeLast24' && 'Last 24 Months'}
            </button>
          ))}
        </div>

        {/* Graph Component */}
        <div className="h-[300px] w-full flex items-center justify-center">
          {getGraphData().length === 0 ? (
            <div className="flex flex-col items-center justify-center w-full">
              <FiBarChart2 className="text-6xl text-slate-300 mb-2" />
              <div className="text-gray-400 text-center">No graph data available for this period.</div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={getGraphData()} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis 
                  dataKey="month" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  dy={10}
                />
                <YAxis 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{ fill: '#64748b', fontSize: 12 }}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  // eslint-disable-next-line @typescript-eslint/no-explicit-any
                  formatter={(value: any) => [`$${value}`, "Income"]}                
                />
                <defs>
                  <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Area 
                  type="monotone" 
                  dataKey="income" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#colorIncome)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </section>
  );
}
