import { useEffect, useState } from 'react';
import fileFacade from '../api/fileFacade';
import { useParams, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiFileText, FiX } from 'react-icons/fi';
import type { FileRecord } from '../types/FileRecords';

export default function ViewFilePage() {
    const { borrowerId } = useParams<{ borrowerId: string }>();
    const navigate = useNavigate();
    
    const [loading, setLoading] = useState(true);
    const [fileRecords, setFileRecords] = useState<FileRecord[]>([]);
    const [fileSignedUrls, setFileSignedUrls] = useState<string[]>([]);
    const [selectedFileIndex, setSelectedFileIndex] = useState<number | null>(null);

    useEffect(() => {
        const fetchFiles = async () => {
            setLoading(true);
            try {
                if (!borrowerId) return;
                
                const fetchedFiles = await fileFacade.getFilesForBorrower(borrowerId);
                if (fetchedFiles.length > 0) {
                    const signedUrls = await fileFacade.getSignedUrlsForFiles(fetchedFiles);
                    setFileSignedUrls(signedUrls);
                }
                setFileRecords(fetchedFiles);
            } catch (error) {
                console.error('Error fetching files:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchFiles();
    }, [borrowerId]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-gray-500 animate-pulse font-medium">Loading borrower files...</div>
            </div>
        );
    }

    if (!borrowerId) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-red-500 font-medium bg-red-50 px-6 py-4 rounded-lg">Invalid borrower ID.</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 p-6 md:p-10">
            <div className="max-w-6xl mx-auto">
                
                {/* HEADER WITH BACK ARROW */}
                <div className="flex items-center gap-4 mb-8">
                    <button 
                        onClick={() => navigate(-1)} 
                        className="p-2.5 bg-white border border-slate-200 hover:bg-slate-50 hover:border-slate-300 rounded-full transition-all text-slate-600 shadow-sm"
                        aria-label="Go back"
                    >
                        <FiArrowLeft className="text-xl" />
                    </button>
                    <div>
                        <h2 className="text-2xl font-bold text-slate-800 m-0">Borrower Documents</h2>
                        <p className="text-slate-500 text-sm mt-1 font-mono">ID: {borrowerId}</p>
                    </div>
                </div>
                
                {/* THE CARD GRID */}
                {fileRecords.length === 0 ? (
                    <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
                        <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
                            <FiFileText className="text-3xl" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-700">No documents found</h3>
                        <p className="text-slate-500 mt-1">This borrower hasn't uploaded any files yet.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        {fileRecords.map((record, index) => (
                            <button 
                                key={record.id || index}
                                onClick={() => setSelectedFileIndex(index)}
                                className="group relative bg-white border border-slate-200 rounded-xl p-5 flex flex-col items-start hover:shadow-md hover:border-blue-300 hover:-translate-y-1 transition-all duration-200 text-left focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                {/* Top Row: Icon & Badge */}
                                <div className="w-full flex justify-between items-start mb-4">
                                    <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300 shadow-sm">
                                        <FiFileText className="text-2xl" />
                                    </div>
                                    
                                    <span className="text-[10px] bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md font-semibold uppercase tracking-wider border border-slate-200">
                                        {record.classification 
                                            ? record.classification.replace('_', ' ') 
                                            : 'DOCUMENT'}
                                    </span>
                                </div>

                                {/* Bottom Row: Title & Date */}
                                <h3 className="font-semibold text-slate-800 w-full truncate text-sm leading-tight" title={record.fileName}>
                                    {record.fileName || `Document ${index + 1}`}
                                </h3>
                                
                                <p className="text-xs text-slate-400 mt-1.5 font-medium">
                                    {record.createdAt 
                                        ? `Uploaded ${new Date(record.createdAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}` 
                                        : 'Click to view document'}
                                </p>
                                
                                {/* Hover Arrow */}
                                <div className="absolute bottom-5 right-5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 text-blue-500">
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                </div>
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {/* THE DOCUMENT VIEWER MODAL */}
            {selectedFileIndex !== null && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 sm:p-6 animate-in fade-in duration-200">
                    <div className="bg-white w-full max-w-5xl h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
                        
                        {/* Modal Header */}
                        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-white">
                            <div>
                                <h3 className="text-lg font-semibold text-slate-800">
                                    {fileRecords[selectedFileIndex]?.fileName || 'Document Viewer'}
                                </h3>
                                <p className="text-sm text-slate-500 capitalize">
                                    {fileRecords[selectedFileIndex]?.classification?.replace('_', ' ') || 'Document'}
                                </p>
                            </div>
                            <button 
                                onClick={() => setSelectedFileIndex(null)}
                                className="p-2 bg-slate-100 text-slate-500 hover:text-slate-700 hover:bg-slate-200 rounded-full transition-colors"
                            >
                                <FiX className="text-xl" />
                            </button>
                        </div>

                        {/* Modal Content (iFrame) */}
                        <div className="flex-1 w-full bg-slate-100 relative">
                            {fileSignedUrls[selectedFileIndex] ? (
                                <iframe
                                    src={fileSignedUrls[selectedFileIndex]}
                                    title={fileRecords[selectedFileIndex]?.fileName || 'Document Viewer'}
                                    className="w-full h-full border-0"
                                    sandbox="allow-same-origin allow-scripts"
                                />
                            ) : (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-500">
                                    <FiFileText className="text-4xl text-slate-300 mb-3" />
                                    <p>Failed to load document URL.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}