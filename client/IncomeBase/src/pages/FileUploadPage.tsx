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

  const zipCode = sessionStorage.getItem('verified_zip');

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
        link_token: token,
        zip_code: zipCode,
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
    <div className="upload-container">
      <h1>Upload Your Documents</h1>
      <p>Please upload your bank statements and W2s for analysis.</p>
      
      <div className="file-input-group">
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          accept=".pdf,.jpg,.jpeg,.png"
          disabled={uploading || submitting}
        />
      </div>

      <div className="file-list">
        {files.length > 0 && (
          <ul>
            {files.map((file, idx) => (
              <li key={idx}>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</li>
            ))}
          </ul>
        )}
      </div>

      {error && <p className="error-message">{error}</p>}

      <button
        onClick={handleUploadAndSubmit}
        disabled={uploading || submitting || files.length === 0}
      >
        {uploading ? 'Uploading...' : submitting ? 'Processing...' : 'Submit Documents'}
      </button>
    </div>
  );
};

export default FileUploadPage;
