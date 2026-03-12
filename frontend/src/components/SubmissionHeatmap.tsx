import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";

type HeatmapData = {
    date: string;
    count: number;
};

const SubmissionsHeatmap = ({ data }: { data: HeatmapData[] }) => {

    const startDate = new Date();
    startDate.setFullYear(startDate.getFullYear() - 1);

    const endDate = new Date();

    return (
        <div className="bg-gray-800 p-6 rounded-xl">
            <h2 className="text-white text-lg mb-4">
                Submission Activity
            </h2>

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