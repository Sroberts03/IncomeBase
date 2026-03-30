import { useState, useEffect } from 'react';
import type { BorrowerDetails } from '../types/BorrowerDetails';
import LinkEmail from '../types/LinkEmail';
import { useAuth } from '../context/AuthContext';
import lenderFacade from '../api/lenderFacade';

type Props = {
    borrowerDetails: BorrowerDetails;
    token: string;
    sendEmail: (emailSubject: string, emailContent: string, borrowerId: string, token: string) => void;
    setEmailVisible: (visible: boolean) => void;
};

export default function SendEmailModal({ borrowerDetails, token, sendEmail, setEmailVisible }: Props) {
    const { user } = useAuth();
    const [emailSubject, setEmailSubject] = useState('Document Request');
    const [lenderRole, setLenderRole] = useState('');
    const [lenderOrg, setLenderOrg] = useState('');
    const [isMessageEdited, setIsMessageEdited] = useState(false);
    const [emailContent, setEmailContent] = useState('');

    useEffect(() => {
        const fetchLenderInfo = async () => {
            if (!user) return;
            try {
                const data = await lenderFacade.getLenderInfo();
                if (data) {
                    if (data.role) setLenderRole(data.role);
                    if (data.organization) setLenderOrg(data.organization);
                }
            } catch (err) {
                console.error('Failed to fetch lender info from server:', err);
            }
        };

        fetchLenderInfo();
    }, [user]);

    useEffect(() => {
        if (!isMessageEdited) {
            setEmailContent(
                LinkEmail(borrowerDetails, token, user?.user_metadata?.display_name, lenderRole, lenderOrg)
            );
        }
    }, [lenderRole, lenderOrg, isMessageEdited, borrowerDetails, token, user]);

    const handleMessageChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setIsMessageEdited(true);
        setEmailContent(e.target.value);
    };

    return (
        // Added flex-col to parent, removed padding on overlay for mobile full-screen
        <div className="fixed inset-0 z-50 flex flex-col sm:items-center sm:justify-center bg-black/50 backdrop-blur-sm sm:p-4 transition-all">
            {/* Modal Container */}
            {/* Sizing changed to viewport percentages (90vw, 85vh) and full-screen on mobile (w-full h-full) */}
            <div className="bg-white rounded-none sm:rounded-2xl shadow-2xl w-full h-full sm:w-[90vw] sm:max-w-5xl sm:h-[85vh] flex flex-col overflow-hidden relative">
                
                {/* Header */}
                <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4 bg-white shrink-0">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600 font-bold text-lg">
                            {borrowerDetails.fullName ? borrowerDetails.fullName[0].toUpperCase() : 'B'}
                        </div>
                        <div className="flex flex-col">
                            <span className="font-semibold text-gray-900 text-sm">{borrowerDetails.fullName || 'Borrower'}</span>
                            <span className="text-xs text-gray-500">{borrowerDetails.email || 'No email provided'}</span>
                        </div>
                    </div>
                    <button
                        className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full w-8 h-8 flex items-center justify-center transition-colors focus:outline-none"
                        onClick={() => setEmailVisible(false)}
                        aria-label="Close modal"
                    >
                        <svg className="w-5 h-5" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                            <path d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>

                {/* Email Form */}
                {/* Increased pb to account for fixed button container */}
                <div className="flex-1 flex flex-col p-6 gap-4 bg-gray-50/30 overflow-y-auto pb-28 sm:pb-32">
                    <div className="flex flex-col sm:flex-row gap-4 mb-2">
                        <div className="flex-1">
                            <label htmlFor="organization" className="text-sm font-medium text-gray-700 block mb-1">Organization</label>
                            <input
                                id="organization"
                                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all text-base text-gray-800 placeholder:text-gray-400 shadow-sm"
                                placeholder="E.g. Acme Lending"
                                value={lenderOrg}
                                onChange={e => setLenderOrg(e.target.value)}
                            />
                        </div>
                        <div className="flex-1">
                            <label htmlFor="role" className="text-sm font-medium text-gray-700 block mb-1">Role</label>
                            <input
                                id="role"
                                className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all text-base text-gray-800 placeholder:text-gray-400 shadow-sm"
                                placeholder="E.g. Loan Officer"
                                value={lenderRole}
                                onChange={e => setLenderRole(e.target.value)}
                            />
                        </div>
                    </div>

                    <label htmlFor="subject" className="text-sm font-medium text-gray-700 -mb-2">Subject</label>
                    <input
                        id="subject"
                        className="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all text-base text-gray-800 placeholder:text-gray-400 shadow-sm"
                        placeholder="Enter message subject"
                        value={emailSubject}
                        onChange={e => setEmailSubject(e.target.value)}
                    />
                    
                    <label htmlFor="message" className="text-sm font-medium text-gray-700 -mb-2 mt-2">Message</label>
                    <textarea
                        id="message"
                        className="w-full flex-1 px-4 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all text-base text-gray-800 placeholder:text-gray-400 resize-none shadow-sm"
                        placeholder="Write your message..."
                        value={emailContent}
                        onChange={handleMessageChange}
                    />
                    
                    {/* Fixed Action Button Container */}
                    {/* Positioned absolute at bottom to stay above content when typing */}
                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-white border-t border-gray-100 mt-auto sm:rounded-b-2xl">
                        <button
                            className="w-full py-3 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white rounded-xl font-medium text-base shadow-sm shadow-blue-600/20 transition-all focus:outline-none focus:ring-4 focus:ring-blue-500/20"
                            onClick={() => sendEmail(emailSubject, emailContent, borrowerDetails.borrowerId, token)}
                        >
                            Send Message
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}