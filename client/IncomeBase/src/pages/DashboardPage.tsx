import React, { useEffect, useState } from 'react';
import lenderFacade from '../api/lenderFacade';
import { useAuth } from '../context/AuthContext';

interface Stats {
  total_borrowers: number;
  needs_link_creation: number;
  link_created: number;
  docs_submitted: number;
  completed: number;
}

interface Borrower {
  borrower_id: string;
  full_name: string;
  email: string;
  status: string;
  created_at: string;
}

const DashboardPage: React.FC = () => {
  const { user, signOut } = useAuth();
  const [stats, setStats] = useState<Stats | null>(null);
  const [borrowers, setBorrowers] = useState<Borrower[]>([]);
  const [loading, setLoading] = useState(true);

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
      const response = await lenderFacade.generateLink({ borrower_id: borrowerId });
      alert(`Link generated! Token: ${response.link_token}`);
      // Refresh borrowers list to update status
      const borrowersData = await lenderFacade.getBorrowers();
      setBorrowers(borrowersData.borrowers);
    } catch (error) {
      console.error('Error generating link:', error);
    }
  };

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div className="dashboard-container">
      <header>
        <h1>Lender Dashboard</h1>
        <div className="user-info">
          <span>{user?.email}</span>
          <button onClick={signOut}>Sign Out</button>
        </div>
      </header>

      {stats && (
        <section className="stats-grid">
          <div className="stat-card">
            <h3>Total Borrowers</h3>
            <p>{stats.total_borrowers}</p>
          </div>
          <div className="stat-card">
            <h3>Needs Link</h3>
            <p>{stats.needs_link_creation}</p>
          </div>
          <div className="stat-card">
            <h3>Link Created</h3>
            <p>{stats.link_created}</p>
          </div>
          <div className="stat-card">
            <h3>Docs Submitted</h3>
            <p>{stats.docs_submitted}</p>
          </div>
          <div className="stat-card">
            <h3>Completed</h3>
            <p>{stats.completed}</p>
          </div>
        </section>
      )}

      <section className="borrower-list">
        <h2>Borrowers</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Status</th>
              <th>Created At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {borrowers.map((borrower) => (
              <tr key={borrower.borrower_id}>
                <td>{borrower.full_name}</td>
                <td>{borrower.email}</td>
                <td>{borrower.status}</td>
                <td>{new Date(borrower.created_at).toLocaleDateString()}</td>
                <td>
                  {borrower.status === 'Needs Link Creation' && (
                    <button onClick={() => handleGenerateLink(borrower.borrower_id)}>
                      Generate Link
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default DashboardPage;
