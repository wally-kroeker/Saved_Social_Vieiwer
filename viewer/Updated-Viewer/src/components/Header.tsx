
import React from "react";
import { ThemeToggle } from "./ThemeToggle";

const Header: React.FC = () => {
  return (
    <header className="w-full py-4 px-6 flex items-center justify-between border-b border-border dark:border-gray-800">
      <div className="flex items-center">
        <h1 className="text-xl font-bold">Social Media Content Viewer</h1>
      </div>
      <div>
        <ThemeToggle />
      </div>
    </header>
  );
};

export default Header;
