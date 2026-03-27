import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const Header: React.FC = () => {
  const { session, isLoading, signOut } = useAuth();

  return (
    <header className="w-full bg-white shadow-sm py-4 px-6 flex items-center justify-between shadow-bottom shadow-gray-800">
      <div className="flex items-center gap-2">
        <Link to="/" className="text-2xl font-extrabold text-blue-700 tracking-tight hover:text-blue-900 transition">
          IncomeBase
        </Link>
      </div>
      <nav className="flex items-center gap-4">
        {!isLoading && session ? (
          <>
            <Link
              to="/dashboard"
              className="text-blue-600 hover:text-blue-800 font-semibold px-4 py-2 rounded transition"
            >
              Dashboard
            </Link>
            <button
              onClick={signOut}
              className="text-blue-600 hover:text-blue-800 font-semibold px-4 py-2 rounded transition"
            >
              Sign Out
            </button>
          </>
        ) : !isLoading ? (
          <Link
            to="/login"
            className="text-blue-600 hover:text-blue-800 font-semibold px-4 py-2 rounded transition"
          >
            Login
          </Link>
        ) : null}
      </nav>
    </header>
  );
};

export default Header;
