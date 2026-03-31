import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiCheckCircle, FiCopy, FiDownload, FiFileText } from 'react-icons/fi';
import type { BorrowerDetails } from '../../types/BorrowerDetails';

interface BorrowerHeaderSectionProps {
  borrowerDetails: BorrowerDetails | null;
  token: string | null;
  baseUrl: string;
  statusBadgeStyles: Record<string, string>;
  handlePrint: () => void;
  handleViewFiles: () => void;
  actions: Array<{ label: string, onClick: () => void, borrowerStatus: string }>;
  handleGenerateLink: () => void;
}

const STATUS_DOT: Record<string, string> = {
  'Analysis Completed':         'bg-indigo-500',
  'Analysis Flagged For Review':'bg-amber-500',
  'Analysis Failed':            'bg-red-500',
  'Analyzing':                  'bg-violet-400 animate-pulse',
  'Docs Submitted':             'bg-green-500',
  'Docs Not Submitted':         'bg-orange-400',
  'Link Created':               'bg-blue-400',
  'Needs Link Creation':        'bg-slate-400',
};

export default function BorrowerHeaderSection({
  borrowerDetails,
  token,
  baseUrl,
  statusBadgeStyles,
  handlePrint,
  handleViewFiles,
  actions,
  handleGenerateLink
}: BorrowerHeaderSectionProps) {
  const navigate = useNavigate();
  const [copiedId, setCopiedId] = useState(false);
  const [copiedDocLink, setCopiedDocLink] = useState(false);

  const truncateId = (id?: string) => {
    if (!id || id.length < 8) return id || '';
    return id.slice(0, 6) + '...' + id.slice(-4);
  };

  const handleCopyId = () => {
    if (borrowerDetails?.borrowerId) {
      navigator.clipboard.writeText(borrowerDetails.borrowerId);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  const handleCopyDocLink = () => {
    if (token) {
      navigator.clipboard.writeText(`${baseUrl}/upload/${token}`);
      setCopiedDocLink(true);
      setTimeout(() => setCopiedDocLink(false), 2000);
    }
  };

  const currentAction = actions.find(a => a.borrowerStatus === borrowerDetails?.status);
  const isAnalyzing = borrowerDetails?.status === 'Analyzing';
  const hasFiles =
    borrowerDetails?.status === 'Docs Submitted' ||
    borrowerDetails?.status === 'Analysis Completed' ||
    borrowerDetails?.status === 'Analysis Failed' ||
    borrowerDetails?.status === 'Analysis Flagged For Review' ||
    borrowerDetails?.status === 'Analyzing';
  const hasExport =
    borrowerDetails?.status === 'Analysis Completed' ||
    borrowerDetails?.status === 'Analysis Flagged For Review';

  const statusDot = STATUS_DOT[borrowerDetails?.status ?? ''] ?? 'bg-slate-400';

  return (
    <section className="max-w-4xl mx-auto px-4 pt-6 pb-5">
      {/* Back nav */}
      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 font-medium transition mb-5 print:hidden"
      >
        <FiArrowLeft size={15} />
        Back to Dashboard
      </button>

      {/* Main header row */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">

        {/* ── Left: Identity block ── */}
        <div className="flex flex-col gap-2 min-w-0">
          {/* Name + status */}
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold text-gray-900 truncate">
              {borrowerDetails?.fullName || 'Borrower'}
            </h1>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${statusBadgeStyles[borrowerDetails?.status ?? ''] || 'bg-gray-100 text-gray-500 border border-gray-200'}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${statusDot}`} />
              {borrowerDetails?.status}
            </span>
          </div>

          {/* Meta row: ID + doc link */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Borrower ID chip */}
            <button
              onClick={handleCopyId}
              title="Copy full ID"
              className="inline-flex items-center gap-1.5 bg-slate-100 hover:bg-slate-200 text-slate-500 font-mono text-xs px-2.5 py-1 rounded-md transition"
            >
              <span>ID: {truncateId(borrowerDetails?.borrowerId)}</span>
              {copiedId
                ? <FiCheckCircle size={11} className="text-green-500" />
                : <FiCopy size={11} />
              }
            </button>

            {/* Doc link chip */}
            {token ? (
              <div className="inline-flex items-center gap-1 bg-blue-50 border border-blue-100 px-2.5 py-1 rounded-md">
                <Link
                  to={`/upload/${token}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline font-mono text-xs font-semibold truncate max-w-[180px]"
                >
                  {`/upload/`}{token.slice(0, 6)}…{token.slice(-4)}
                </Link>
                <button
                  onClick={handleCopyDocLink}
                  className="ml-0.5 p-0.5 rounded hover:bg-blue-100 text-blue-400 hover:text-blue-700 transition"
                  title="Copy document link"
                >
                  {copiedDocLink
                    ? <FiCheckCircle size={11} className="text-green-500" />
                    : <FiCopy size={11} />
                  }
                </button>
              </div>
            ) : (
              <span className="text-xs text-slate-400">No doc link</span>
            )}
          </div>
        </div>

        {/* ── Right: Actions ── */}
        <div className="flex items-center gap-2 print:hidden flex-shrink-0">
          {hasExport && (
            <button
              onClick={handlePrint}
              className="inline-flex items-center gap-1.5 bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 font-medium px-3.5 py-2 rounded-lg text-sm shadow-sm transition"
            >
              <FiDownload size={14} />
              Export PDF
            </button>
          )}
          {hasFiles && (
            <button
              onClick={handleViewFiles}
              className="inline-flex items-center gap-1.5 bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 hover:border-slate-300 font-medium px-3.5 py-2 rounded-lg text-sm shadow-sm transition"
            >
              <FiFileText size={14} />
              View Files
            </button>
          )}
          <button
            onClick={currentAction?.onClick || handleGenerateLink}
            disabled={isAnalyzing}
            className={`inline-flex items-center gap-1.5 font-semibold px-4 py-2 rounded-lg text-sm shadow-sm transition ${
              isAnalyzing
                ? 'bg-indigo-300 text-white cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
            }`}
          >
            {currentAction?.label || 'Generate Link'}
          </button>
        </div>
      </div>
    </section>
  );
}
