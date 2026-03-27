import React, { useEffect, useState } from 'react';
import lenderFacade from '../api/lenderFacade';
import { useAuth } from '../context/AuthContext';
import { FiUsers, FiLink, FiFileText, FiCheckCircle, FiUserPlus, FiLogOut, FiSettings, FiSearch, FiChevronDown } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';

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
  const navigator = useNavigate();
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
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);

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

  const filteredBorrowers = borrowers.filter(b => {
    const matchesSearch = b.fullName.toLowerCase().includes(searchTerm.toLowerCase()) || b.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'All' || b.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Status options for filter
  const statusOptions = ['All', 'Needs Link Creation', 'Link Created', 'Docs Not Submitted', 'Docs Submitted', 'Analysis Completed', 'Analyzing', 'Analysis Failed', 'Analysis Flagged For Review'];

  // Status badge color map (softer palette)
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

  // Stat card config
  const statCards = stats ? [
    {
      label: 'Total Borrowers',
      value: stats.totalBorrowers,
      icon: <FiUsers className="text-blue-500 text-xl" />, bg: 'bg-blue-50', border: 'border-blue-100'
    },
    {
      label: 'Needs Link',
      value: stats.needsLinkCreation,
      icon: <FiLink className="text-yellow-500 text-xl" />, bg: 'bg-yellow-50', border: 'border-yellow-100'
    },
    {
      label: 'Link Created',
      value: stats.linkCreated,
      icon: <FiLink className="text-blue-400 text-xl" />, bg: 'bg-blue-50', border: 'border-blue-100'
    },
    {
      label: 'Docs Submitted',
      value: stats.docsSubmitted,
      icon: <FiFileText className="text-green-500 text-xl" />, bg: 'bg-green-50', border: 'border-green-100'
    },
    {
      label: 'Completed',
      value: stats.completed,
      icon: <FiCheckCircle className="text-emerald-600 text-xl" />, bg: 'bg-emerald-50', border: 'border-emerald-100'
    },
  ] : [];

  const handleBorrowerClick = (borrowerId: string) => {
    navigator(`/borrower/${borrowerId}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8 font-sans">
      {/* Header with nav, avatar, and settings */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 max-w-[1400px] mx-auto">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Lender Dashboard</h1>
          <p className="text-gray-600 mt-1 text-base">{timeOfDayGreeting(currentHour)}, <span className="font-semibold">{user?.user_metadata?.full_name}</span>!</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-px h-8 bg-gray-200 mx-2" />
          {/* User avatar (placeholder) */}
          <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-bold text-lg">
            {user?.user_metadata?.full_name?.[0] || 'U'}
          </div>
          <button className="ml-2 text-gray-500 hover:text-gray-700 p-2 rounded-full transition"><FiSettings className="text-xl" /></button>
          <button className="ml-1 text-gray-500 hover:text-gray-700 p-2 rounded-full transition"><FiLogOut className="text-xl" /></button>
        </div>
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

      {/* Main content container with max-width */}
      <main className="max-w-[1400px] mx-auto">
        {/* Stat Cards */}
        {stats && (
          <section className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 mb-10">
            {statCards.map((card) => (
              <div
                key={card.label}
                className={`flex items-center gap-4 p-5 rounded-xl border ${card.border} ${card.bg} shadow-sm transition`}
              >
                <div className="flex-shrink-0">{card.icon}</div>
                <div className="flex flex-col items-start">
                  <span className="text-xs font-medium text-gray-500 mb-1 tracking-wide" style={{ letterSpacing: '0.02em' }}>{card.label}</span>
                  <span className="text-3xl font-extrabold text-gray-900 leading-tight" style={{ fontFamily: 'Inter, Geist, sans-serif' }}>{card.value}</span>
                </div>
              </div>
            ))}
          </section>
        )}

        {/* Search and Filter Bar */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
          <div className="flex items-center gap-2 w-full md:w-auto">
            <div className="relative w-full md:w-64">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg" />
              <input
                type="text"
                placeholder="Search borrowers..."
                className="pl-10 pr-4 py-2 w-full border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white text-sm"
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="relative">
              <button
                className="flex items-center gap-1 px-3 py-2 border border-gray-200 rounded-lg bg-white text-sm text-gray-700 hover:bg-gray-100 transition"
                onClick={() => setShowStatusDropdown(v => !v)}
                type="button"
              >
                Status: {statusFilter}
                <FiChevronDown className="ml-1 text-gray-400" />
              </button>
              {showStatusDropdown && (
                <div className="absolute left-0 mt-2 w-44 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                  {statusOptions.map(option => (
                    <button
                      key={option}
                      className={`block w-full text-left px-4 py-2 text-sm hover:bg-blue-50 ${option === statusFilter ? 'font-semibold text-blue-600' : 'text-gray-700'}`}
                      onClick={() => { setStatusFilter(option); setShowStatusDropdown(false); }}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
          <button
            onClick={() => setShowCreateBorrowerModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-full shadow-xl transition"
          >
            <FiUserPlus className="text-lg" />
            Create New Borrower
          </button>
        </div>

        {/* Borrowers Table */}
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
                {filteredBorrowers.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-400 text-lg">No borrowers found.</td>
                  </tr>
                ) : (
                  filteredBorrowers.map((borrower) => (
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
      </main>
    </div>
  );
};

export default DashboardPage;
