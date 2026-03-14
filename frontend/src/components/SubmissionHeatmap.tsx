import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
import type {HeatmapData, Stats } from "../constants/config";

const SubmissionsHeatmap = ({
  data,
  stats,
}: {
  data: HeatmapData[];
  stats: Stats;
}) => {
  const startDate = new Date();
  startDate.setFullYear(startDate.getFullYear() - 1);

  const endDate = new Date();

  return (
    <div className="bg-gray-800 p-6 rounded-xl shadow-lg h-110">

      {/* Title */}
      <h2 className="text-white text-2xl font-bold mb-8">
        Submission Activity
      </h2>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-4 gap-4 mb-8">

        <StatCard label="Max Submissions" value={stats.max_submission} />
        <StatCard label="Avg Submissions" value={stats.avg_submission} />
        <StatCard label="Max Streak" value={stats.max_streak} />
        <StatCard label="Current Streak" value={stats.current_streak} />

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
          if (!value) return "No submissions";
          return `${value.count} submissions on ${value.date}`;
        }}
      />

    </div>
  );
};

const StatCard = ({ label, value }: { label: string; value: number }) => {
  return (
    <div className="bg-gray-900 p-5 rounded-lg text-center hover:scale-105 transition duration-200">
      <p className="text-gray-400 text-sm mb-1">{label}</p>
      <p className="text-white text-2xl font-bold">{value}</p>
    </div>
  );
};

export default SubmissionsHeatmap;