import { FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';
import type { BorrowerDetails } from '../../types/BorrowerDetails';

interface BorrowerAnalysisSummaryProps {
  borrowerDetails: BorrowerDetails | null;
}

export default function BorrowerAnalysisSummary({ borrowerDetails }: BorrowerAnalysisSummaryProps) {
  return (
    <>
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
                <li key={idx} className="flex items-center gap-2 text-red-700">
                  <FiAlertTriangle className="text-red-500 flex-shrink-0" /> {factor}
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2 text-green-700">
              <FiCheckCircle className="text-green-500 flex-shrink-0" /> No Risk Factors Detected
            </div>
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
                <li key={idx} className="flex items-center gap-2 text-red-700">
                  <FiAlertTriangle className="text-red-500 flex-shrink-0" /> {deposit}
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex items-center gap-2 text-green-700">
              <FiCheckCircle className="text-green-500 flex-shrink-0" /> No Anomalous Deposits Detected
            </div>
          )}
        </div>
      </section>
    </>
  );
}
