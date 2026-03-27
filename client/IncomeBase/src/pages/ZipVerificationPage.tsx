import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import lenderFacade from '../api/lenderFacade';

const ZipVerificationPage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [zipCode, setZipCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const response = await lenderFacade.verifyZip({
        linkToken: token,
        zipCode: zipCode,
      });

      if (response.valid) {
        // Store verified zip in session storage to use during final submission
        sessionStorage.setItem('verifiedZip', zipCode);
        navigate(`/upload/${token}`);
      } else {
        setError(response.message);
      }
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.response?.data?.message || 'Verification failed. Please check your link.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-blue-100 py-8 px-2">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 flex flex-col items-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Verify Your Identity</h1>
        <p className="text-gray-600 mb-6 text-center">Please enter the zip code you provided to your lender to access the document upload page.</p>
        <form onSubmit={handleVerify} className="w-full flex flex-col gap-4">
          <div>
            <label htmlFor="zipCode" className="block text-gray-700 font-medium mb-1">Zip Code</label>
            <input
              type="text"
              id="zipCode"
              value={zipCode}
              onChange={(e) => setZipCode(e.target.value)}
              placeholder="e.g. 12345"
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          {error && <p className="w-full text-center text-red-600 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition disabled:opacity-60"
          >
            {loading ? 'Verifying...' : 'Continue'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ZipVerificationPage;
