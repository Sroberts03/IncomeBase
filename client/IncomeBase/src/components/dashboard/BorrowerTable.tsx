export interface Borrower {
  borrowerId: string;
  fullName: string;
  email: string;
  status: string;
  createdAt: string;
}

interface BorrowerTableProps {
  borrowers: Borrower[];
  handleBorrowerClick: (borrowerId: string) => void;
  statusBadgeStyles: Record<string, string>;
}

export default function BorrowerTable({ borrowers, handleBorrowerClick, statusBadgeStyles }: BorrowerTableProps) {
  return (
    <section className="bg-white rounded-xl shadow p-0 border border-gray-100 overflow-hidden">
      <h2 className="text-xl font-semibold text-gray-700 px-6 pt-6 pb-2">Borrowers</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-100">
          <thead className="bg-gray-50 shadow-lg">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Created At</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-50">
            {borrowers.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-gray-400 text-lg">No borrowers found.</td>
              </tr>
            ) : (
              borrowers.map((borrower) => (
                <tr 
                  key={borrower.borrowerId} 
                  className="hover:bg-gray-50 transition"
                  onClick={() => handleBorrowerClick(borrower.borrowerId)}
                  style={{ cursor: 'pointer' }}
                >
                    <td className="px-6 py-4 whitespace-nowrap text-gray-900 font-bold text-base">{borrower.fullName}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-700 text-sm">{borrower.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${statusBadgeStyles[borrower.status] || 'bg-gray-50 text-gray-500 border border-gray-100'}`}>
                        {borrower.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-sm">{new Date(borrower.createdAt).toLocaleDateString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
