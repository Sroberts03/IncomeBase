import React, { useEffect, useState } from 'react';
import lenderFacade from '../api/lenderFacade';
import { useAuth } from '../context/AuthContext';

interface Stats {
  totalBorrowers: number;
  needsLinkCreation: number;
  linkCreated: number;
  docsSubmitted: number;
  completed: number;
}

interface Borrower {
  borrowerId: string;
  fullName: string;
  email: string;
  status: string;
  createdAt: string;
}

const timeOfDayGreeting = (currentHour: number) => {
  if (currentHour < 12) return 'Good morning';
  if (currentHour < 18) return 'Good afternoon';
  return 'Good evening';
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [borrowers, setBorrowers] = useState<Borrower[]>([]);
  const [loading, setLoading] = useState(true);
  const currentHour = new Date().getHours();
  const [showCreateBorrowerModal, setShowCreateBorrowerModal] = useState(false);
  const [newBorrowerName, setNewBorrowerName] = useState('');
  const [newBorrowerEmail, setNewBorrowerEmail] = useState('');
  const [newBorrowerZip, setNewBorrowerZip] = useState('');
  const [creatingBorrower, setCreatingBorrower] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, borrowersData] = await Promise.all([
          lenderFacade.getDashboardStats(),
          lenderFacade.getBorrowers(),
        ]);
        setStats(statsData);
        setBorrowers(borrowersData.borrowers);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    }; 

    fetchData();
  }, []);

  const handleGenerateLink = async (borrowerId: string) => {
    try {
      const response = await lenderFacade.generateLink({ borrowerId: borrowerId });
      alert(`Link generated! Token: ${response.linkToken}`);
      // Refresh borrowers list to update status
      const borrowersData = await lenderFacade.getBorrowers();
      setBorrowers(borrowersData.borrowers);
    } catch (error) {
      console.error('Error generating link:', error);
    }
  };

  const handleCreateBorrower = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingBorrower(true);
    try {
      await lenderFacade.createBorrower({
        fullName: newBorrowerName,
        email: newBorrowerEmail,
        zipCode: newBorrowerZip,
      });
      setShowCreateBorrowerModal(false);
      setNewBorrowerName('');
      setNewBorrowerEmail('');
      setNewBorrowerZip('');
      // Refresh dashboard data after creating borrower
      const [statsData, borrowersData] = await Promise.all([
        lenderFacade.getDashboardStats(),
        lenderFacade.getBorrowers(),
      ]);
      setStats(statsData);
      setBorrowers(borrowersData.borrowers);
      alert('Borrower created successfully!');
    } catch (error) {
      alert('Error creating borrower.');
      console.error('Error creating borrower:', error);
    } finally {
      setCreatingBorrower(false);
    }
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen text-lg text-gray-500">Loading dashboard...</div>;

  return (

    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Lender Dashboard</h1>
          <p className="text-gray-600 mt-1">{timeOfDayGreeting(currentHour)}, {user?.displayName}!</p>
        </div>
        <button
          onClick={() => setShowCreateBorrowerModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-lg shadow transition"
        >
          Create New Borrower
        </button>
            {/* Create Borrower Modal */}
            {showCreateBorrowerModal && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/30 backdrop-blur-md">
                <div className="bg-white rounded-xl shadow-xl p-8 w-full max-w-md relative">
                  <button
                    className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-2xl font-bold"
                    onClick={() => setShowCreateBorrowerModal(false)}
                    aria-label="Close"
                  >
                    &times;
                  </button>
                  <h2 className="text-2xl font-bold mb-4 text-gray-800">Create New Borrower</h2>
                  <form onSubmit={handleCreateBorrower} className="flex flex-col gap-4">
                    <div>
                      <label className="block text-gray-700 font-medium mb-1">Full Name</label>
                      <input
                        type="text"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={newBorrowerName}
                        onChange={e => setNewBorrowerName(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-gray-700 font-medium mb-1">Email</label>
                      <input
                        type="email"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={newBorrowerEmail}
                        onChange={e => setNewBorrowerEmail(e.target.value)}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-gray-700 font-medium mb-1">ZIP Code</label>
                      <input
                        type="text"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
                        value={newBorrowerZip}
                        onChange={e => setNewBorrowerZip(e.target.value)}
                        required
                        pattern="\d{5}(-\d{4})?"
                        placeholder="e.g. 12345 or 12345-6789"
                      />
                    </div>
                    <div className="flex justify-end gap-2 mt-2">
                      <button
                        type="button"
                        className="px-4 py-2 rounded bg-gray-200 text-gray-700 hover:bg-gray-300"
                        onClick={() => setShowCreateBorrowerModal(false)}
                        disabled={creatingBorrower}
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-5 py-2 rounded bg-blue-600 text-white font-semibold hover:bg-blue-700 transition disabled:opacity-60"
                        disabled={creatingBorrower}
                      >
                        {creatingBorrower ? 'Creating...' : 'Create'}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
      </header>

      {stats && (
        <section className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-10">
          <div className="bg-white rounded-xl shadow p-5 flex flex-col items-center">
            <h3 className="text-sm text-gray-500 font-medium mb-1">Total Borrowers</h3>
            <p className="text-2xl font-bold text-blue-600">{stats.totalBorrowers}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5 flex flex-col items-center">
            <h3 className="text-sm text-gray-500 font-medium mb-1">Needs Link</h3>
            <p className="text-2xl font-bold text-yellow-500">{stats.needsLinkCreation}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5 flex flex-col items-center">
            <h3 className="text-sm text-gray-500 font-medium mb-1">Link Created</h3>
            <p className="text-2xl font-bold text-blue-400">{stats.linkCreated}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5 flex flex-col items-center">
            <h3 className="text-sm text-gray-500 font-medium mb-1">Docs Submitted</h3>
            <p className="text-2xl font-bold text-green-500">{stats.docsSubmitted}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5 flex flex-col items-center">
            <h3 className="text-sm text-gray-500 font-medium mb-1">Completed</h3>
            <p className="text-2xl font-bold text-emerald-600">{stats.completed}</p>
          </div>
        </section>
      )}

      <section className="bg-white rounded-xl shadow p-6">
        <h2 className="text-xl font-semibold text-gray-700 mb-4">Borrowers</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {borrowers.map((borrower) => (
                <tr key={borrower.borrowerId}>
                  <td className="px-4 py-2 whitespace-nowrap text-gray-800">{borrower.fullName}</td>
                  <td className="px-4 py-2 whitespace-nowrap text-gray-700">{borrower.email}</td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    <span className={
                      borrower.status === 'Needs Link Creation'
                        ? 'inline-block px-2 py-1 text-xs font-semibold rounded bg-yellow-100 text-yellow-800'
                        : borrower.status === 'Completed'
                        ? 'inline-block px-2 py-1 text-xs font-semibold rounded bg-emerald-100 text-emerald-800'
                        : 'inline-block px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800'
                    }>
                      {borrower.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 whitespace-nowrap text-gray-500">{new Date(borrower.createdAt).toLocaleDateString()}</td>
                  <td className="px-4 py-2 whitespace-nowrap">
                    {borrower.status === 'Needs Link Creation' && (
                      <button
                        onClick={() => handleGenerateLink(borrower.borrowerId)}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs font-medium transition"
                      >
                        Generate Link
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default DashboardPage;
