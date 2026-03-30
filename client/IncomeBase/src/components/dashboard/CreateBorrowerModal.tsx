import React, { useState } from 'react';
import { FiZap } from 'react-icons/fi';
import toast from 'react-hot-toast';
import lenderFacade from '../../api/lenderFacade';

interface CreateBorrowerModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function CreateBorrowerModal({ onClose, onSuccess }: CreateBorrowerModalProps) {
  const [newBorrowerName, setNewBorrowerName] = useState('');
  const [newBorrowerEmail, setNewBorrowerEmail] = useState('');
  const [newBorrowerZip, setNewBorrowerZip] = useState('');
  const [creatingBorrower, setCreatingBorrower] = useState(false);

  const handleCreateBorrower = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingBorrower(true);
    try {
      await lenderFacade.createBorrower({
        fullName: newBorrowerName,
        email: newBorrowerEmail,
        zipCode: newBorrowerZip,
      });
      setNewBorrowerName('');
      setNewBorrowerEmail('');
      setNewBorrowerZip('');
      toast.success('Borrower created successfully!');
      onSuccess();
      onClose();
    } catch (error) {
      toast.error('Error creating borrower.');
      console.error('Error creating borrower:', error);
    } finally {
      setCreatingBorrower(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/30 backdrop-blur-md">
      <div className="bg-white rounded-xl shadow-xl p-8 w-full max-w-md relative">
        <button
          className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 text-2xl font-bold"
          onClick={onClose}
          aria-label="Close"
        >
          &times;
        </button>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Create New Borrower</h2>
          <button 
            type="button" 
            onClick={() => {
              setNewBorrowerName("John Doe");
              setNewBorrowerEmail("samr72003@gmail.com");
              setNewBorrowerZip("84054");
            }}
            className="text-yellow-500 hover:text-yellow-600 bg-yellow-50 hover:bg-yellow-100 p-2 rounded-full transition-colors mr-8"
            title="Demo Magic Autofill"
          >
            <FiZap className="w-5 h-5" />
          </button>
        </div>
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
              onClick={onClose}
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
  );
}
