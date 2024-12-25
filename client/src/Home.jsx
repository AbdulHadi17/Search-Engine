"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";
import { Link } from "react-router-dom";

export default function Home() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.classList.add("dark");
        } else {
            document.documentElement.classList.remove("dark");
        }
    }, [isDarkMode]);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsSearching(true);
        setError("");

        try {
            const response = await fetch("/api/get-query-result/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: query }), // Sending the query as JSON in the body
            });

            if (!response.ok) {
                const errorResponse = await response.json();
                console.error("Error Response:", errorResponse);
                throw new Error(errorResponse.message || "An error occurred while searching.");
            }

            const data = await response.json();
            setResults(data.ranked_results || []);
        } catch (err) {
            console.error("Error:", err.message);
            setError(err.message);
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-900 dark:to-blue-900 transition-colors duration-500">
            <div className="absolute inset-0 bg-grid-slate-200 dark:bg-grid-slate-700 [mask-image:linear-gradient(to_bottom,white,transparent)] pointer-events-none"></div>
            <main className="relative flex min-h-screen flex-col items-center justify-start p-24">
                <Button
                    variant="outline"
                    size="icon"
                    className="absolute top-4 right-4"
                    onClick={() => setIsDarkMode(!isDarkMode)}
                >
                    {isDarkMode ? (
                        <Sun className="h-[1.2rem] w-[1.2rem]" />
                    ) : (
                        <Moon className="h-[1.2rem] w-[1.2rem]" />
                    )}
                </Button>

                <h1 className="text-4xl font-bold mb-8 text-gray-800 dark:text-white">
                    Job Posting
                </h1>

                <form onSubmit={handleSearch} className="w-full max-w-2xl mb-8">
                    <div className="flex gap-2">
                        <Input
                            type="text"
                            placeholder="Enter your search query"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            className="flex-grow border-white bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm"
                        />
                        <Button
                            type="submit"
                            disabled={isSearching}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                        >
                            {isSearching ? "Searching..." : "Search"}
                        </Button>
                    </div>
                </form>

                {error && (
                    <div className="text-red-500 mb-4">
                        {error}
                    </div>
                )}

                <div className="w-full max-w-2xl mb-8">
                    {results.map((result) => (
                        <div
                            key={result.id}
                            className="mb-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm p-4 rounded-lg"
                        >
                            <h2 className="text-xl font-semibold text-blue-600 dark:text-blue-400">
                                {result.title}
                            </h2>
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                                {result.snippet}
                            </p>
                        </div>
                    ))}
                </div>

                <Link to="/add-doc">
                    <Button className="bg-green-600 hover:bg-green-700 text-white">
                        Add Document
                    </Button>
                </Link>
            </main>
        </div>
    );
}
