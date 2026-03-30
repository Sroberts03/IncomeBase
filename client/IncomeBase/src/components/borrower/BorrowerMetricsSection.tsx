import type { BorrowerDetails } from '../../types/BorrowerDetails';

interface BorrowerMetricsSectionProps {
  borrowerDetails: BorrowerDetails | null;
  monthlyIncome: number;
  stabilityScore: number;
  confidenceScore: number;
  getScoreColor: (score: number) => string;
}

export default function BorrowerMetricsSection({
  borrowerDetails,
  monthlyIncome,
  stabilityScore,
  confidenceScore,
  getScoreColor
}: BorrowerMetricsSectionProps) {
  return (
    <>
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
    </>
  );
}
