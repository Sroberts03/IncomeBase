import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiCheckCircle, FiCopy, FiDownload } from 'react-icons/fi';
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
    return id.slice(0, 4) + '...' + id.slice(-4);
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

  return (
    <section className="max-w-4xl mx-auto px-4 pt-8 pb-4">
      <div className="max-w-4xl mx-auto px-4 mb-6 print:hidden">
        <button 
          onClick={() => navigate('/dashboard')}
          className="flex items-center text-blue-600 hover:text-blue-800 font-medium transition"
        >
          <FiArrowLeft className="mr-2" />
          Back to Dashboard
        </button>
      </div>
      <div className="flex flex-col md:flex-row items-center md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-4 min-w-0">
          <div className="flex flex-col min-w-0">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 min-w-0">
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 truncate">{borrowerDetails?.fullName || 'Borrower'}</h1>
              <span className={`ml-0 sm:ml-3 px-3 py-1 rounded-full text-sm font-semibold ${statusBadgeStyles[borrowerDetails?.status ?? ''] 
                || 'bg-gray-100 text-gray-500 border border-gray-200'}`}>{borrowerDetails?.status}</span>
            </div>
            {/* Document Link (truncated, blue, copyable, under name, in container) */}
            {token ? (
              <div className="flex items-center mt-1">
                <div className="flex items-center bg-blue-50 border border-blue-100 px-3 py-1.5 rounded-md min-w-0">
                  <Link
                    to={`/upload/${token}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline font-mono text-xs font-semibold truncate max-w-[220px]"
                    style={{display:'inline-block'}}
                  >
                    {`${baseUrl}/upload/`}{token.slice(0, 6)}...{token.slice(-6)}
                  </Link>
                  <button
                    onClick={handleCopyDocLink}
                    className="ml-1 p-1 rounded hover:bg-blue-100 text-blue-400 hover:text-blue-700 transition"
                    title="Copy document link"
                    tabIndex={0}
                  >
                    {copiedDocLink ? <FiCheckCircle className="text-green-500 text-xs" /> : <FiCopy className="text-xs" />}
                  </button>
                </div>
              </div>
            ) : (
              <span className="text-xs text-gray-400 mt-1">No Doc Link Available</span>
            )}
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
                {copiedId ? <FiCheckCircle className="text-green-500 text-xs" /> : <FiCopy className="text-xs" />}
              </button>
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
        <div className="flex items-center gap-2 mt-2 md:mt-0 print:hidden">
          { (borrowerDetails?.status === "Analysis Completed" || borrowerDetails?.status === "Analysis Flagged For Review") && (
            <button 
              className="bg-white border text-blue-600 hover:bg-blue-50 border-blue-200 font-semibold px-4 py-3 rounded-full shadow-sm transition flex items-center gap-2"
              onClick={() => handlePrint()}
            >
              <FiDownload />
              Export PDF
            </button>
          )}
          { borrowerDetails?.status === "Docs Submitted" 
            || borrowerDetails?.status === "Analysis Completed" 
            || borrowerDetails?.status === "Analysis Failed"
            || borrowerDetails?.status === "Analysis Flagged For Review" 
            || borrowerDetails?.status === "Analyzing" ? (
            <button 
              className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-3 rounded-full shadow-xl transition text-base"
              onClick={handleViewFiles}
            >
              View Files
            </button>
          ) : null }
          <button 
            className={
              borrowerDetails?.status === "Analyzing" ? "bg-blue-200 text-white font-semibold px-6 py-3 rounded-full shadow-xl transition text-base" 
                : "bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-full shadow-xl transition text-base"
            }
            onClick={actions.find(action => action.borrowerStatus === borrowerDetails?.status)?.onClick || handleGenerateLink}
          >
            {actions.find(action => action.borrowerStatus === borrowerDetails?.status)?.label || 'Generate Link'}
          </button>
        </div>
      </div>
    </section>
  );
}
