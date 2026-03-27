import { useEffect, useState } from 'react';
import lenderFacade from '../api/lenderFacade';
import { useParams, useNavigate } from 'react-router-dom';
import type { BorrowerDetails } from '../types/BorrowerDetails';
import { FiArrowLeft, FiAlertTriangle, FiCheckCircle, FiCopy } from 'react-icons/fi';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

export default function BorrowersDetailPage() {
  const { borrowerId } = useParams();
  const navigate = useNavigate();
  const [borrowerDetails, setBorrowerDetails] = useState<BorrowerDetails | null>(null);
  const [activeGraphTab, setActiveGraphTab] = useState<string>('incomeYtd');

  useEffect(() => {
    const fetchBorrowerDetails = async () => {
      try {
        const details = await lenderFacade.getBorrowerDetails(borrowerId!);
        setBorrowerDetails(details);
      } catch (error) {
        console.error('Error fetching borrower details:', error);
      }
    };
    fetchBorrowerDetails();
  }, [borrowerId]);

  // Color helpers for scores
  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-50 text-green-700 border-green-200';
    if (score >= 0.5) return 'bg-yellow-50 text-yellow-700 border-yellow-200';
    return 'bg-red-50 text-red-700 border-red-200';
  };

  // Status badge color
  const statusBadgeStyles: Record<string, string> = {
    'Needs Link Creation': 'bg-yellow-50 text-yellow-700 border border-yellow-200',
    'Link Created': 'bg-blue-50 text-blue-700 border border-blue-200',
    'Docs Not Submitted': 'bg-gray-50 text-gray-500 border border-gray-200',
    'Docs Submitted': 'bg-green-50 text-green-700 border border-green-200',
    'Analysis Completed': 'bg-indigo-50 text-indigo-700 border border-indigo-200',
    'Completed': 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    'System Error': 'bg-red-50 text-red-700 border border-red-200',
  };

  const getGraphData = () => {
    switch (activeGraphTab) {
      case 'incomeYtd':
        return borrowerDetails?.analysis?.incomeYtd || [];
      case 'incomeLast6':
        return borrowerDetails?.analysis?.incomeLast6 || [];
      case 'incomeLast12':
        return borrowerDetails?.analysis?.incomeLast12 || [];
      case 'incomeLast24':
        return borrowerDetails?.analysis?.incomeLast24 || [];
      default:
        return [];
    }
  }


  // Key metrics for cards
  const monthlyIncome = borrowerDetails?.analysis?.monthlyAverageIncome ?? 0;
  const stabilityScore = borrowerDetails?.analysis?.incomeStabilityScore ?? 0;
  const confidenceScore = borrowerDetails?.analysis?.confidenceScore ?? 0;


  // Helper to truncate UUIDs (e.g., 0998...515b)
  const truncateId = (id?: string) => {
    if (!id || id.length < 8) return id || '';
    return id.slice(0, 4) + '...' + id.slice(-4);
  };

  // Copy to clipboard handler with feedback
  const [copied, setCopied] = useState(false);
  const handleCopyId = () => {
    if (borrowerDetails?.borrowerId) {
      navigator.clipboard.writeText(borrowerDetails.borrowerId);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    }
  };

  return (
    <div className="bg-gray-50 min-h-screen py-8">
      {/* Header Hero Section */}
      <section className="max-w-4xl mx-auto px-4 pt-8 pb-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <button
              onClick={() => navigate(-1)}
              className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 mr-2"
              title="Back to Dashboard"
            >
              <FiArrowLeft className="text-xl" />
            </button>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 truncate">{borrowerDetails?.fullName || 'Borrower'}</h1>
              <span className={`ml-0 sm:ml-3 px-3 py-1 rounded-full text-sm font-semibold ${statusBadgeStyles[borrowerDetails?.status ?? ''] || 'bg-gray-100 text-gray-500 border border-gray-200'}`}>{borrowerDetails?.status}</span>
            </div>
            <span className="ml-0 sm:ml-4 text-xs text-gray-400 font-mono flex items-center gap-1 relative">
              ID: {truncateId(borrowerDetails?.borrowerId)}
              {borrowerDetails?.borrowerId && (
                <button
                  onClick={handleCopyId}
                  className="ml-1 p-1 rounded hover:bg-gray-200 text-gray-400 hover:text-gray-700 transition"
                  title="Copy full ID"
                  tabIndex={0}
                >
                  <FiCopy className="text-xs" />
                </button>
              )}
              {copied && (
                <span className="absolute left-full ml-2 px-2 py-1 rounded bg-gray-800 text-white text-xs font-semibold shadow z-10 animate-fade-in-out" style={{whiteSpace:'nowrap'}}>Copied!</span>
              )}
            </span>
          <style>{`
          @keyframes fadeInOut {
            0% { opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { opacity: 0; }
          }
          .animate-fade-in-out {
            animation: fadeInOut 1.2s;
          }
          `}</style>
          </div>
          <div className="flex items-center gap-2 mt-2 md:mt-0">
            <button className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg shadow transition text-base">
              Generate Link
            </button>
          </div>
        </div>
      </section>

      {/* Highlight Cards */}
      <section className="max-w-4xl mx-auto px-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        <div className="rounded-xl border border-blue-100 bg-blue-50 p-5 flex flex-col items-start">
          <span className="text-xs text-gray-500 font-medium mb-2">Monthly Avg Income</span>
          <span className="text-2xl font-bold text-blue-700">${monthlyIncome.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </div>
        <div className={`rounded-xl border p-5 flex flex-col items-start ${getScoreColor(stabilityScore)}`}>
          <span className="text-xs text-gray-500 font-medium mb-2">Income Stability Score</span>
          <span className="text-2xl font-bold">{(stabilityScore * 100).toFixed(0)}%</span>
        </div>
        <div className={`rounded-xl border p-5 flex flex-col items-start ${getScoreColor(confidenceScore)}`}>
          <span className="text-xs text-gray-500 font-medium mb-2">Confidence Score</span>
          <span className="text-2xl font-bold">{(confidenceScore * 100).toFixed(0)}%</span>
        </div>
      </section>

      {/* Key Metrics Table (Grid) */}
      <section className="max-w-4xl mx-auto px-4 mb-8">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Key Metrics</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3 bg-white rounded-xl border border-gray-100 p-6">
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Recurring Income %</span>
            <span className="font-bold text-gray-900">{((borrowerDetails?.analysis?.recurringIncomePercentage ?? 0) * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Income Trend</span>
            <span className="font-bold text-gray-900">{borrowerDetails?.analysis?.incomeTrend || '-'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Largest Deposit Source</span>
            <span className="font-bold text-gray-900">{borrowerDetails?.analysis?.largestDepositSource || '-'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Expense to Income Ratio</span>
            <span className="font-bold text-gray-900">{((borrowerDetails?.analysis?.expenseToIncomeRatio ?? 0) * 100).toFixed(2)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-500">Net Burn Rate</span>
            <span className="font-bold text-gray-900">${(borrowerDetails?.analysis?.netBurnRate ?? 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-500">NSF Count Total</span>
            <span className="font-bold text-gray-900">{borrowerDetails?.analysis?.nsfCountTotal ?? 0}</span>
          </div>
        </div>
      </section>

      {/* Income Graph with Tabs */}
      <section className="max-w-4xl mx-auto px-4 mb-8">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Income Graph</h2>
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          
          {/* Your existing tabs */}
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

          {/* THE GRAPH COMPONENT */}
          <div className="h-[300px] w-full flex items-center justify-center">
            {getGraphData().length === 0 ? (
              <div className="text-gray-400 text-center w-full">No graph data available for this period.</div>
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


      {/* Analysis Summary */}
      <section className="max-w-4xl mx-auto px-4 mb-8">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Analysis Summary</h2>
        <div className="bg-white rounded-xl border border-gray-100 p-6 text-gray-800">
          {borrowerDetails?.analysis?.analysisSummary || <span className="text-gray-400">No summary available.</span>}
        </div>
      </section>

      {/* Risk Factors */}
      <section className="max-w-4xl mx-auto px-4 mb-8">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Risk Factors</h2>
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          {borrowerDetails?.analysis?.riskFactors && borrowerDetails.analysis.riskFactors.length > 0 ? (
            <ul className="space-y-2">
              {borrowerDetails.analysis.riskFactors.map((factor, idx) => (
                <li key={idx} className="flex items-center gap-2 text-red-700"><FiAlertTriangle className="text-red-500" /> {factor}</li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2 text-green-700"><FiCheckCircle className="text-green-500" /> No Risk Factors Detected</div>
          )}
        </div>
      </section>

      {/* Anomalous Deposits */}
      <section className="max-w-4xl mx-auto px-4 mb-12">
        <h2 className="text-lg font-semibold text-gray-700 mb-3">Anomalous Deposits</h2>
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          {borrowerDetails?.analysis?.anomalousDeposits && borrowerDetails.analysis.anomalousDeposits.length > 0 ? (
            <ul className="space-y-2">
              {borrowerDetails.analysis.anomalousDeposits.map((deposit, idx) => (
                <li key={idx} className="flex items-center gap-2 text-red-700"><FiAlertTriangle className="text-red-500" /> {deposit}</li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2 text-green-700"><FiCheckCircle className="text-green-500" /> No Anomalous Deposits Detected</div>
          )}
        </div>
      </section>
    </div>
  );
}