import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";

type HeatmapData = {
    date: string;
    count: number;
};

type Stats = {
    max_submission: number;
    min_submission: number;
    avg_submission: number;
    max_streak: number;
    current_streak: number;
};

const SubmissionsHeatmap = ({ data, stats }: { data: HeatmapData[], stats: Stats }) => {

    const startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 1);

    const endDate = new Date();

    return (
        <div className="bg-gray-800 p-6 rounded-xl h-110">
            <h2 className="text-white text-2xl font-bold mb-8">
                Submission Activity
            </h2>

            {/* Stats Section */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">

                <div className="bg-gray-900 p-4 rounded-lg text-center">
                    <p className="text-gray-400 text-sm">Max Submissions</p>
                    <p className="text-white font-semibold">{stats.max_submission}</p>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg text-center">
                    <p className="text-gray-400 text-sm">Min Submissions</p>
                    <p className="text-white font-semibold">{stats.min_submission}</p>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg text-center">
                    <p className="text-gray-400 text-sm">Avg Submissions</p>
                    <p className="text-white font-semibold">{stats.avg_submission}</p>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg text-center">
                    <p className="text-gray-400 text-sm">Max Streak</p>
                    <p className="text-white font-semibold">{stats.max_streak}</p>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg text-center">
                    <p className="text-gray-400 text-sm">Current Streak</p>
                    <p className="text-white font-semibold">{stats.current_streak}</p>
                </div>

            </div>

            {/* Heatmap */}
            <CalendarHeatmap
                startDate={startDate}
                endDate={endDate}
                values={data}
                classForValue={(value) => {
                    if (!value) return "color-empty";
                    if (value.count >= 5) return "color-github-4";
                    if (value.count >= 3) return "color-github-3";
                    if (value.count >= 1) return "color-github-2";
                    return "color-empty";
                }}
                titleForValue={(value) => {
                    if (!value) return "no submissions"
                    return `${value.count} submissions on ${value.date}`;
                }}
            />
        </div>
    );
};

export default SubmissionsHeatmap;