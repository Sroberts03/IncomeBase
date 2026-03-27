import React from 'react';

const SuccessPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-blue-100 py-8 px-2">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 flex flex-col items-center">
        <h1 className="text-3xl font-bold text-green-600 mb-4">Success!</h1>
        <p className="text-gray-700 text-lg mb-6 text-center">
          Your documents have been submitted for analysis.<br />
          You will be notified when your results are ready.
        </p>
        <svg className="w-16 h-16 text-green-400 mb-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
        <a href="/" className="mt-2 text-blue-600 hover:underline">Return Home</a>
      </div>
    </div>
  );
};

export default SuccessPage;
