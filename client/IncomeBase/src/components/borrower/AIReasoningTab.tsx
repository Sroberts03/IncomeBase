import { useEffect, useState } from 'react';
import fileFacade, { type ReasoningLog } from '../../api/fileFacade';
import { FiCpu, FiClock, FiFile, FiChevronDown, FiChevronUp, FiAlertCircle } from 'react-icons/fi';

interface AIReasoningTabProps {
  borrowerId: string;
}

const AGENT_META: Record<string, { label: string; color: string; bg: string; border: string }> = {
  file_review:      { label: 'File Review',       color: 'text-blue-700',   bg: 'bg-blue-50',   border: 'border-blue-200' },
  classifier:       { label: 'Classifier',         color: 'text-violet-700', bg: 'bg-violet-50', border: 'border-violet-200' },
  extractor:        { label: 'Extractor',          color: 'text-amber-700',  bg: 'bg-amber-50',  border: 'border-amber-200' },
  analyzer:         { label: 'Analyzer',           color: 'text-emerald-700',bg: 'bg-emerald-50',border: 'border-emerald-200' },
  reasoning_review: { label: 'Reasoning Review',  color: 'text-rose-700',   bg: 'bg-rose-50',   border: 'border-rose-200' },
};

function AgentBadge({ agent }: { agent: string }) {
  const meta = AGENT_META[agent] ?? { label: agent, color: 'text-gray-600', bg: 'bg-gray-100', border: 'border-gray-200' };
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${meta.color} ${meta.bg} ${meta.border}`}>
      <FiCpu size={11} />
      {meta.label}
    </span>
  );
}

function ReasoningCard({ log }: { log: ReasoningLog }) {
  const [expanded, setExpanded] = useState(false);
  const date = new Date(log.created_at);
  const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  const formattedTime = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  const isLong = log.raw_reasoning.length > 300;
  const displayText = isLong && !expanded ? log.raw_reasoning.slice(0, 300) + '…' : log.raw_reasoning;

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden">
      {/* Card Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-gray-50 bg-gray-50/60">
        <div className="flex items-center gap-3">
          <AgentBadge agent={log.agent} />
          {log.file_id && (
            <span className="flex items-center gap-1 text-xs text-gray-400 font-mono">
              <FiFile size={11} />
              {log.file_id.slice(0, 8)}…
            </span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-400">
          <FiClock size={11} />
          <span>{formattedDate} · {formattedTime}</span>
        </div>
      </div>

      {/* Reasoning Text */}
      <div className="px-5 py-4">
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{displayText}</p>
        {isLong && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-3 flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            {expanded ? <><FiChevronUp size={13} /> Show less</> : <><FiChevronDown size={13} /> Show more</>}
          </button>
        )}
      </div>
    </div>
  );
}

export default function AIReasoningTab({ borrowerId }: AIReasoningTabProps) {
  const [logs, setLogs] = useState<ReasoningLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterAgent, setFilterAgent] = useState<string>('all');

  useEffect(() => {
    const fetch = async () => {
      try {
        setLoading(true);
        const data = await fileFacade.getReasoningLogs(borrowerId);
        setLogs(data);
      } catch (err) {
        console.error('Failed to fetch reasoning logs:', err);
        setError('Failed to load AI reasoning logs.');
      } finally {
        setLoading(false);
      }
    };
    fetch();
  }, [borrowerId]);

  const agentTypes = ['all', ...Array.from(new Set(logs.map(l => l.agent)))];
  const filtered = filterAgent === 'all' ? logs : logs.filter(l => l.agent === filterAgent);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-400">Loading AI reasoning logs…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-700 rounded-xl px-5 py-4">
          <FiAlertCircle className="flex-shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 flex flex-col items-center gap-3 text-center">
        <div className="w-14 h-14 rounded-full bg-indigo-50 flex items-center justify-center mb-1">
          <FiCpu size={28} className="text-indigo-300" />
        </div>
        <p className="text-gray-500 font-medium">No AI reasoning logs yet.</p>
        <p className="text-sm text-gray-400">Logs will appear here once files have been processed by the AI pipeline.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 pb-12">
      {/* Header + Filters */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-xs text-gray-400 mt-0.5">{logs.length} log{logs.length !== 1 ? 's' : ''} recorded</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap justify-end">
          {agentTypes.map(agent => (
            <button
              key={agent}
              onClick={() => setFilterAgent(agent)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                filterAgent === agent
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                  : 'bg-white text-gray-500 border-gray-200 hover:border-indigo-300 hover:text-indigo-600'
              }`}
            >
              {agent === 'all' ? 'All Agents' : (AGENT_META[agent]?.label ?? agent)}
            </button>
          ))}
        </div>
      </div>

      {/* Log Cards */}
      {filtered.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">No logs for this agent yet.</p>
      ) : (
        <div className="space-y-3">
          {filtered.map(log => (
            <ReasoningCard key={log.id} log={log} />
          ))}
        </div>
      )}
    </div>
  );
}
