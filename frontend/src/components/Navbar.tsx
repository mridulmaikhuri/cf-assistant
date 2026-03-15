import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-gray-700 text-white px-8 py-4 flex items-center justify-center border-white opacity-80">
      <div className="flex space-x-8 text-lg font-medium justify-center items-center">
        <Link to="/" className="hover:text-blue-400 hover:scale-110 transition">
          Home
        </Link>

        <Link to="/problems" className="hover:text-blue-400 hover:scale-110 transition">
          Problems
        </Link>

        <Link to="/training" className="hover:text-blue-400 hover:scale-110 transition">
          Training
        </Link>

        <Link to="/contest" className="hover:text-blue-400 hover:scale-110 transition">
          Contest
        </Link>

        <Link to="/code-analyzer" className="hover:text-blue-400 hover:scale-110 transition">
          Code Analyzer
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;