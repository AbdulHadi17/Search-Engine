import React, { useState } from "react";
import { IoSearch } from "react-icons/io5";
import searchResults from "./modules/searchResults";

const Home = () => {
  const [hasSearched, setHasSearched] = useState(false);
  const [query, setQuery] = useState("");

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSearch = () => {
    if (!query.trim()) {
      alert("Please enter a valid search query!");
      return;
    }

    // add logic for sending the query to the backend
    
    setHasSearched(true);
  };

  return (
    <div className="w-screen h-screen flex flex-col justify-center items-center bg-slate-950">
      {/* Search Bar */}
      <div className="ml-[10%] mr-[10%] md:ml-[20%] md:mr-[20%] bg-slate-950 shadow-sm shadow-black w-full py-5 justify-center flex rounded-full">
        <input
          placeholder="Search for Jobs..."
          value={query}
          onChange={handleQueryChange}
          type="text"
          className="bg-white w-[80%] px-4 py-2 rounded-l-2xl outline-none border border-b-4 shadow-black shadow-sm"
        />
        <button
          onClick={handleSearch}
          className="bg-red-700 px-4 py-2 border border-red-600 rounded-r-2xl flex justify-center items-center"
        >
          <IoSearch className="text-white text-2xl hover:scale-105" />
        </button>
      </div>

      {/* Search Results */}
      {hasSearched && (
        <div className="h-[90vh] bg-slate-50 w-full py-4 md:px-12 px-6 overflow-y-auto">
          <div className="px-7 text-gray-700">
            Fetched {searchResults.totalResults} sites in 0.009 seconds
          </div>
          <div className="mt-2 w-full h-full flex flex-col p-4 gap-3">
            {searchResults.results.map((result) => (
              <div
                key={result.id}
                className="border p-3 bg-white rounded shadow-md"
              >
                <h3 className="text-lg font-bold line-clamp-1">{result.title}</h3>
                <p className="text-sm text-gray-600 line-clamp-2">
                  {result.description}
                </p>
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline mt-2 block line-clamp-1"
                >
                  {result.displayUrl}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
