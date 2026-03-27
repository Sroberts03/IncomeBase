import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import fileFacade from '../api/fileFacade';
import { supabase } from '../api/supabaseClient';

const FileUploadPage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [borrowerId, setBorrowerId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const zipCode = sessionStorage.getItem('verifiedZip');

  useEffect(() => {
    if (!zipCode) {
      navigate(`/verify/${token}`);
      return;
    }

    // Get borrower ID from token (we need it for storage path)
    const fetchBorrowerId = async () => {
      const { data, error } = await supabase
        .from('file_links')
        .select('borrower_id')
        .eq('link_token', token)
        .single();
      
      if (error) {
        setError('Invalid link or session expired.');
      } else {
        setBorrowerId(data.borrower_id);
      }
    };

    fetchBorrowerId();
  }, [token, zipCode, navigate]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUploadAndSubmit = async () => {
    if (!borrowerId || !token || !zipCode) return;
    if (files.length === 0) {
      setError('Please select at least one file.');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      // 1. Upload each file to Supabase Storage
      await Promise.all(files.map(file => fileFacade.uploadFile(borrowerId, file)));
      
      setUploading(false);
      setSubmitting(true);

      // 2. Trigger the backend submission/processing
      const result = await fileFacade.submitFiles({
        linkToken: token,
        zipCode: zipCode,
      });

      console.log('Submission result:', result);
      alert('Documents submitted successfully!');
      navigate('/success');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message || 'Failed to upload or submit files.');
    } finally {
      setUploading(false);
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-blue-100 py-8 px-2">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 flex flex-col items-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Upload Your Documents</h1>
        <p className="text-gray-600 mb-6 text-center">Please upload your bank statements and W2s for analysis.</p>

        <div className="w-full mb-4">
          <input
            type="file"
            multiple
            onChange={handleFileChange}
            accept=".pdf,.jpg,.jpeg,.png"
            disabled={uploading || submitting}
            className="block w-full text-sm text-gray-700 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>

        {files.length > 0 && (
          <div className="w-full mb-4">
            <ul className="text-sm text-gray-700">
              {files.map((file, idx) => (
                <li key={idx} className="flex justify-between border-b border-gray-100 py-1">
                  <span>{file.name}</span>
                  <span className="text-gray-400">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {error && <p className="w-full text-center text-red-600 text-sm mb-4">{error}</p>}

        <button
          onClick={handleUploadAndSubmit}
          disabled={uploading || submitting || files.length === 0}
          className="w-full py-2 px-4 rounded-lg bg-blue-600 text-white font-semibold shadow hover:bg-blue-700 transition disabled:opacity-60 mb-2"
        >
          {uploading ? 'Uploading...' : submitting ? 'Processing...' : 'Submit Documents'}
        </button>
      </div>
    </div>
  );
};

export default FileUploadPage;
