import { useEffect, useState } from "react";

import type { Problem } from "../constants/config";
import { API_BASE_URL, USER_HANDLE } from "../constants/config";

function Problems() {
    const [problems, setProblems] = useState<Problem[]>([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const problemsPerPage = 10;
    const lastProblemIndex = currentPage * problemsPerPage;
    const firstProblemIndex = lastProblemIndex - problemsPerPage;
    const currentProblems = problems.slice(firstProblemIndex, lastProblemIndex);
    const totalPages = Math.ceil(problems.length / problemsPerPage)

    useEffect(() => {
        const fetchRecommendedProblems = async () => {
            try {
                setLoading(true);
                setError("");

                const res = await fetch(`${API_BASE_URL}/user/problems/${USER_HANDLE}`)
                if (!res.ok) {
                    throw new Error("Failed to fetch recommendation")
                }

                const data = await res.json();
                setProblems(data.recommendedProblems);

                setCurrentPage(1);
            } catch (err) {
                setError("Could not load recommended problems");
            } finally {
                setLoading(false);
            }
        };
        fetchRecommendedProblems();
    }, [])

    if (loading) {
        return (
            <div className="text-white">
                Loading recommendations...
            </div>
        )
    }

    if (error) {
        return (
            <div className="text-red-400">
                {error}
            </div>
        )
    }

    return (
        <div className="bg-gray-700 rounded-xl p-6 shadow-lg">
            <h2 className="text-4xl font-semibold text-white mb-10 mt-5 text-center">
                Recommended Problems
            </h2>

            <div className="space-y-4">
                {
                    currentProblems.map((problem) => (
                        <div
                            key={`${problem.contestId}-${problem.index}`}
                            className="bg-gray-800 p-4 rounded-lg border border-gray-700"
                        >
                            <div className="flex justify-between items-start gap-4">
                                <div>
                                    <a
                                        href={problem.link}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="text-blue-400 hover:underline text-lg font-semibold"
                                    >
                                        {problem.name}
                                    </a>
                                    <div className="text-sm text-gray-300 mt-1">
                                        Rating: {problem.rating}
                                    </div>
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {
                                            problem.tags.map((tag) => (
                                                <span
                                                    key={tag}
                                                    className="px-2 py-1 text-xs rounded-full bg-blue-600 text-white"
                                                >
                                                    {tag}
                                                </span>
                                            ))
                                        }
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                }
            </div>

            <div className="flex justify-center items-center gap-4 mt-6">
                <button
                    onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
                    disabled={currentPage === 1}
                    className="px-4 py-2 bg-gray-600 text-white rounded disabled:opacity-50"
                >
                    Prev
                </button>
                <span className="text-white">
                    Page: {currentPage} of {totalPages}
                </span>
                <button
                    onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 bg-gray-600 text-white rounded disabled:opacity-50"
                >
                    Next
                </button>
            </div>
        </div>
    )
}

export default Problems