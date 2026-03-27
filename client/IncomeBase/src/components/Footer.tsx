import React from "react";

const Footer: React.FC = () => (
  <footer 
  className="
  w-full 
  bg-gray-50 
  border-t 
  border-gray-200 
  py-4 px-6 
  text-center 
  text-sm 
  text-gray-500
  shadow-top
  "
  >
    &copy; {new Date().getFullYear()} IncomeBase. All rights reserved.
  </footer>
);

export default Footer;
