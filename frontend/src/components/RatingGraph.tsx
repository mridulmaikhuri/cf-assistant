import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid
} from "recharts";
import type { RatingEntry, RatingStats } from "../constants/config";

const RatingGraph = ({
    data,
    stats
}: {
    data: RatingEntry[]
    stats: RatingStats
}) => {

    const chartData = data.map((contest, index) => ({
        contest: index + 1,
        rating: contest.newRating,
        name: contest.contestName,
        rank: contest.rank,
        delta: contest.newRating - contest.oldRating
    }));

    const CustomTooltip = ({ active, payload }: any) => {
        if (!active || !payload || !payload.length) return null;

        const data = payload[0].payload;
        const deltaColor = data.delta >= 0 ? "text-green-400" : "text-red-400";

        return (
            <div className="bg-gray-900 p-3 rounded-lg border border-gray-700">
                <p className="text-white mb-1">{data.name}</p>

                <p className="text-gray-300 text-sm">
                    Rating: <span className="text-green-400">{data.rating}</span>
                </p>

                <p className="text-gray-300 text-sm">
                    Rank: <span className="text-yellow-400">{data.rank}</span>
                </p>

                <p className="text-gray-300 text-sm">
                    delta: <span className={deltaColor}>
                        {data.delta > 0 ? "+" : ""}{data.delta}
                    </span>
                </p>

            </div>
        );
    };

    return (
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg">

            <h2 className="text-white text-2xl font-bold mb-6">
                Rating Progress
            </h2>

            {/* Stats Section */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">

                <StatCard label="Max Rating Gain" value={`+${stats.max_delta}`} />

                <StatCard label="Avg Rating Change" value={stats.avg_delta} />

                <StatCard label="Total Contests" value={stats.total_contest} />

            </div>

            {/* Rating Graph */}
            <ResponsiveContainer width="100%" height={350}>
                <LineChart data={chartData}>

                    <CartesianGrid stroke="#374151" strokeDasharray="3 3" />

                    <XAxis
                        dataKey="contest"
                        stroke="#9CA3AF"
                        label={{
                            value: "Contests",
                            position: "insideBottom",
                            offset: -5,
                            fill: "#9CA3AF"
                        }}
                    />

                    <YAxis
                        stroke="#9CA3AF"
                        domain={["dataMin - 50", "dataMax + 50"]}
                        label={{
                            value: "Rating",
                            angle: -90,
                            position: "insideLeft",
                            fill: "#9CA3AF"
                        }}
                    />

                    <Tooltip content={<CustomTooltip />} />

                    <Line
                        type="monotone"
                        dataKey="rating"
                        stroke="#22c55e"
                        strokeWidth={3}
                        dot={false}
                    />

                </LineChart>
            </ResponsiveContainer>

        </div>
    );
};

const StatCard = ({ label, value }: { label: string; value: any }) => {
    return (
        <div className="bg-gray-900 p-5 rounded-lg text-center hover:scale-105 transition">
            <p className="text-gray-400 text-sm mb-1">{label}</p>
            <p className="text-white text-2xl font-bold">{value}</p>
        </div>
    );
};

export default RatingGraph;