import { useEffect, useState, useRef } from 'react';
import lenderFacade from '../api/lenderFacade';
import fileFacade from '../api/fileFacade';
import { useParams, useNavigate } from 'react-router-dom';
import type { BorrowerDetails } from '../types/BorrowerDetails';
import { useReactToPrint } from 'react-to-print';
import BorrowerMetricsSection from '../components/borrower/BorrowerMetricsSection';
import BorrowerAnalysisCharts from '../components/borrower/BorrowerAnalysisCharts';
import BorrowerAnalysisSummary from '../components/borrower/BorrowerAnalysisSummary';
import BorrowerHeaderSection from '../components/borrower/BorrowerHeaderSection';
import AIReasoningTab from '../components/borrower/AIReasoningTab';
import SendEmailModal from '../components/SendEmailModal';
import toast from 'react-hot-toast';
import { FiBarChart2, FiCpu } from 'react-icons/fi';

export default function BorrowersDetailPage() {
  const { borrowerId } = useParams();
  const navigate = useNavigate();
  const [borrowerDetails, setBorrowerDetails] = useState<BorrowerDetails | null>(null);
  const [activeTab, setActiveTab] = useState<'analysis' | 'reasoning'>('analysis');
  const [activeGraphTab, setActiveGraphTab] = useState<string>('incomeYtd');
  const [token, setToken] = useState<string | null>(null);
  const [ loading, setLoading ] = useState(true);
  const baseUrl = import.meta.env.VITE_BASE_URL || '';
  const [emailVisible, setEmailVisible] = useState(false);
  
  const componentRef = useRef<HTMLDivElement>(null);
  const handlePrint = useReactToPrint({
    contentRef: componentRef,
    documentTitle: `IncomeBase_Underwriting_Report_${borrowerId}`,
    pageStyle: `
      @page {
        size: auto;
        margin: 20mm;
      }
      @media print {
        body {
          -webkit-print-color-adjust: exact;
        }
      }
    `
  });
  
  useEffect(() => {
    const fetchBorrowerDetails = async () => {
      setLoading(true);
      try {
        const details = await lenderFacade.getBorrowerDetails(borrowerId!);
        setBorrowerDetails(details);
        setToken(details?.documentLink || null);
        setLoading(false);
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
    'Docs Not Submitted': 'bg-orange-50 text-orange-500 border border-orange-200',
    'Docs Submitted': 'bg-green-50 text-green-700 border border-green-200',
    'Analysis Completed': 'bg-indigo-50 text-indigo-700 border border-indigo-200',
    'Analyzing': 'bg-purple-50 text-purple-400 border border-purple-200',
    'Analysis Failed': 'bg-red-50 text-red-700 border border-red-200',
    'Analysis Flagged For Review': 'bg-red-50 text-red-700 border border-red-200',
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

  const handleGenerateLink = async () => {
    try {
      const result = await lenderFacade.generateLink({borrowerId: borrowerId!});
      setToken(result);
    } catch (error) {
      console.error('Error generating link:', error);
    }
  };

  const handleViewFiles = () => {
    if (borrowerDetails?.status === "Docs Submitted" 
      || borrowerDetails?.status === "Analysis Completed" 
      || borrowerDetails?.status === "Analysis Failed" 
      || borrowerDetails?.status === "Analysis Flagged For Review"
      || borrowerDetails?.status === "Analyzing") {
      navigate(`file/view/${borrowerDetails.borrowerId}`)
    }
    else {
      toast.error('Files are not available until documents have been submitted.');
    }
  }

  const handleAnalyzeFiles = async () => {
    try {
      await fileFacade.analyzeFiles({borrowerId: borrowerId!});
      toast.success('File analysis has been initiated. Please refresh the page after a few moments to see updated results.');
    } catch (error) {
      console.error('Error analyzing files:', error);
      toast.error('An error occurred while analyzing files. Please try again later.');
    }
  };

  const handleSendEmail = async (emailContent: string, emailSubject: string, borrowerId: string, token: string) => {
    try {
      await lenderFacade.sendEmail({
        borrowerId,
        token,
        subject: emailSubject,
        htmlContent: emailContent
      });
      setEmailVisible(false);
      toast.success('Email sent successfully!');
    } catch (err) {
      console.error('Failed to send email:', err);
      toast.error('Failed to send email. Check your console and backend logs for more details.');
    }
  };

  const actions = [
    { label: 'Generate Link', onClick: handleGenerateLink, borrowerStatus: 'Needs Link Creation' },
    { label: 'Email Doc Link', onClick: () => setEmailVisible(true), borrowerStatus: 'Link Created' },
    { label: 'Remind to Submit', onClick: () => setEmailVisible(true), borrowerStatus: 'Docs Not Submitted' },
    { label: 'Run Analysis', onClick: () => toast('Analysis in progress...', { icon: '⏳' }), borrowerStatus: 'Analyzing' },
    { label: 'Run Analysis', onClick: handleAnalyzeFiles, borrowerStatus: 'Docs Submitted' },
    { label: 'Re-run Analysis', onClick: handleAnalyzeFiles, borrowerStatus: 'Analysis Completed' },
    { label: 'Re-run Analysis', onClick: handleAnalyzeFiles, borrowerStatus: 'Analysis Failed' },
    { label: 'Re-run Analysis', onClick: handleAnalyzeFiles, borrowerStatus: 'Analysis Flagged For Review' },
  ];

  return (
    <div className="bg-gray-50 min-h-screen py-8" >
      {loading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-white bg-opacity-70">
          <div className="flex flex-col items-center">
            <svg className="animate-spin h-10 w-10 text-blue-500 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
            <div className="text-gray-500 text-lg font-medium">Loading borrower details...</div>
          </div>
        </div>
      )}
      {emailVisible && (
        <SendEmailModal sendEmail={handleSendEmail} borrowerDetails={borrowerDetails!} token={token!} setEmailVisible={setEmailVisible} />
      )}
      <BorrowerHeaderSection
        borrowerDetails={borrowerDetails}
        token={token}
        baseUrl={baseUrl}
        statusBadgeStyles={statusBadgeStyles}
        handlePrint={handlePrint}
        handleViewFiles={handleViewFiles}
        actions={actions}
        handleGenerateLink={handleGenerateLink}
      />

      {/* Page Tabs */}
      <div className="max-w-4xl mx-auto px-4 mb-6">
        <div className="flex items-center gap-1 bg-white border border-gray-200 rounded-xl p-1 w-fit shadow-sm">
          <button
            id="tab-analysis"
            onClick={() => setActiveTab('analysis')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
              activeTab === 'analysis'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            <FiBarChart2 size={15} />
            Analysis
          </button>
          <button
            id="tab-ai-reasoning"
            onClick={() => setActiveTab('reasoning')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
              activeTab === 'reasoning'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            }`}
          >
            <FiCpu size={15} />
            AI Reasoning
          </button>
        </div>
      </div>

      {/* Tab Panels */}
      {activeTab === 'analysis' && (
        <div ref={componentRef}>
          <BorrowerMetricsSection 
            borrowerDetails={borrowerDetails}
            monthlyIncome={monthlyIncome}
            stabilityScore={stabilityScore}
            confidenceScore={confidenceScore}
            getScoreColor={getScoreColor}
          />

          <BorrowerAnalysisCharts 
            activeGraphTab={activeGraphTab}
            setActiveGraphTab={setActiveGraphTab}
            getGraphData={getGraphData}
          />

          <BorrowerAnalysisSummary 
            borrowerDetails={borrowerDetails}
          />
        </div>
      )}

      {activeTab === 'reasoning' && borrowerId && (
        <AIReasoningTab borrowerId={borrowerId} />
      )}
    </div>
  );
}