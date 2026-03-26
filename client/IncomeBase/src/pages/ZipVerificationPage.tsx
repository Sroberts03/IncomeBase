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
        link_token: token,
        zip_code: zipCode,
      });

      if (response.valid) {
        // Store verified zip in session storage to use during final submission
        sessionStorage.setItem('verified_zip', zipCode);
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
    <div className="zip-verification-container">
      <h1>Verify Your Identity</h1>
      <p>Please enter the zip code you provided to your lender to access the document upload page.</p>
      <form onSubmit={handleVerify}>
        <div className="form-group">
          <label htmlFor="zipCode">Zip Code</label>
          <input
            type="text"
            id="zipCode"
            value={zipCode}
            onChange={(e) => setZipCode(e.target.value)}
            placeholder="e.g. 12345"
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Verifying...' : 'Continue'}
        </button>
      </form>
    </div>
  );
};

export default ZipVerificationPage;
