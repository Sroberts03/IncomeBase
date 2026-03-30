import React, { useState, useRef, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import fileFacade from '../api/fileFacade';

const FileUploadPage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [files, setFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileErrors, setFileErrors] = useState<Record<string, string>>({});
  const navigate = useNavigate();
  const zipCode = sessionStorage.getItem('verifiedZip');

  useEffect(() => {
    if (!zipCode) {
      navigate('/verify/' + token);
    }
  }, [token, zipCode, navigate]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (fileList && fileList.length > 0) {
      setFiles(prev => [...prev, ...Array.from(fileList)]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(prev => [...prev, ...Array.from(e.dataTransfer.files)]);
    }
  };

  const handleRemoveFile = (idx: number) => {
    setFiles(prev => {
      const newFiles = [...prev];
      const removedFile = newFiles.splice(idx, 1)[0];
      if (removedFile) {
        setFileErrors(prevErrors => {
          const newErrors = { ...prevErrors };
          delete newErrors[removedFile.name];
          return newErrors;
        });
      }
      return newFiles;
    });
  };

  const handleBrowseFiles = () => {
    inputRef.current?.click();
  };

  const handleUploadAndSubmit = async () => {
    if (!token || !zipCode) return;
    if (files.length === 0) {
      setError('Please select at least one file.');
      return;
    }

    setUploading(true);
    setError(null);
    setFileErrors({});

    try {
      // 1. Upload each file to Supabase Storage
      const fileUUID = crypto.randomUUID().replace(/-/g, '');
      console.log(`Generated file UUID: ${fileUUID}`);
      await Promise.all(files.map(file => fileFacade.uploadFile(file, zipCode, fileUUID, token)));
      
      setUploading(false);
      setSubmitting(true);

      // 2. Trigger the backend submission/processing
      const result = await fileFacade.submitFiles({
        linkToken: token,
        zipCode: zipCode,
      });

      console.log('Submission result:', result);
      
      const rejectedFiles = result.reviewResults?.filter((r: any) => r.status === 'rejected') || [];
      if (rejectedFiles.length > 0) {
        const errors: Record<string, string> = {};
        const acceptedFileNames = new Set(
          result.reviewResults?.filter((r: any) => r.status === 'approved').map((r: any) => r.fileName) || []
        );
        
        rejectedFiles.forEach((r: any) => {
          if (r.fileName) errors[r.fileName] = r.borrowerMessage || 'File was rejected.';
        });
        
        setFileErrors(errors);
        
        // Remove accepted files from the UI, keep only rejected ones
        setFiles(prev => prev.filter(f => !acceptedFileNames.has(f.name)));
        
        setError('Some documents were not accepted. Please review the errors below.');
      } else {
        alert('Documents submitted successfully!');
        navigate('/success');
      }
      
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

        {/* Drag-and-drop area */}
        <div
          className={`w-full mb-4 border-2 border-dashed rounded-lg transition-colors duration-200 flex flex-col items-center justify-center cursor-pointer ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-blue-300'}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleBrowseFiles}
          style={{ minHeight: 120 }}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            onChange={handleFileChange}
            accept=".pdf,.jpg,.jpeg,.png"
            disabled={uploading || submitting}
            className="hidden"
          />
          <div className="flex flex-col items-center">
            <svg className="w-10 h-10 text-blue-400 mb-2" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M7 16v-4a4 4 0 018 0v4m-4 4v-4m0 0V8m0 4H5m14 0h-4" /></svg>
            <span className="text-gray-500 text-sm">Drag & drop files here or <span className="text-blue-600 underline">browse</span></span>
            <span className="text-xs text-gray-400 mt-1">(PDF, JPG, PNG, JPEG)</span>
          </div>
        </div>

        {/* File list with remove option */}
        {files.length > 0 && (
          <div className="w-full mb-4">
            <ul className="text-sm text-gray-700">
              {files.map((file, idx) => (
                <li key={idx} className="flex flex-col border-b border-gray-100 py-2 gap-1">
                  <div className="flex items-center justify-between w-full">
                    <span className="flex items-center gap-2">
                      {file.type.startsWith('image') ? (
                        <img src={URL.createObjectURL(file)} alt={file.name} className="w-6 h-6 object-cover rounded" />
                      ) : (
                        <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M7 16v-4a4 4 0 018 0v4m-4 4v-4m0 0V8m0 4H5m14 0h-4" /></svg>
                      )}
                      <span>{file.name}</span>
                      {fileErrors[file.name] && (
                        <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                      )}
                    </span>
                    <span className="flex items-center gap-2">
                      <span className="text-gray-400">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                    <button
                      type="button"
                      className="ml-2 text-red-500 hover:text-red-700 text-xs font-semibold px-2 py-1 rounded"
                      onClick={e => { e.stopPropagation(); handleRemoveFile(idx); }}
                      disabled={uploading || submitting}
                    >
                      Remove
                    </button>
                  </span>
                  </div>
                  {fileErrors[file.name] && (
                    <p className="text-sm text-red-600 ml-8 mt-1 border-l-2 border-red-500 pl-2">{fileErrors[file.name]}</p>
                  )}
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
