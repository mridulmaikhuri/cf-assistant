const Navbar = () => {
  return (
    <nav className="bg-gray-700 text-white px-8 py-4 flex items-center justify-center border-white opacity-80">
      {/* Nav Links */}
      <div className="flex space-x-8 text-lg font-medium justify-center items-center">
        <a href="/" className="hover:text-blue-400 hover:scale-110 transition">
          Home
        </a>

        <a href="/problems" className="hover:text-blue-400 hover:scale-110 transition">
          Problems
        </a>

        <a href="/training" className="hover:text-blue-400 hover:scale-110 transition">
          Training
        </a>

        <a href="/contest" className="hover:text-blue-400 hover:scale-110 transition">
          Contest
        </a>

        <a href="/code-analyzer" className="hover:text-blue-400 hover:scale-110 transition">
          Code Analyzer
        </a>
      </div>

    </nav>
  );
};

export default Navbar;