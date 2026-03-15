import { useState, useEffect } from "react";

import { USER_HANDLE, API_BASE_URL } from "../constants/config";
import type { UserData, HeatmapData, Stats, RatingEntry, RatingStats } from "../constants/config";
import UserCard from "../components/UserCard";
import SubmissionsHeatmap from "../components/SubmissionHeatmap";
import RatingGraph from "../components/RatingGraph";

function Home() {
    const [data, setData] = useState<UserData>({
        handle: "",
        profilePhoto: "",
        rating: 0,
        rank: "",
        maxRating: 0,
        maxRank: ""
    });

    const [heatmap, setHeatmap] = useState<HeatmapData[]>([]);

    const [stats, setStats] = useState<Stats>({
        max_submission: 0,
        avg_submission: 0,
        max_streak: 0,
        current_streak: 0
    });

    const [ratingHistory, setRatingHistory] = useState<RatingEntry[]>([]);

    const [ratingStats, setRatingStats] = useState<RatingStats>({
        max_delta: 0,
        avg_delta: 0,
        total_contest: 0
    });

    useEffect(
        () => {
            fetch(`${API_BASE_URL}/user/info/${USER_HANDLE}`)
                .then(res => res.json())
                .then(data => setData(data));
        },
        []
    )

    useEffect(
        () => {
            fetch(`${API_BASE_URL}/user/submission/${USER_HANDLE}`)
                .then(res => res.json())
                .then(data => {
                    setHeatmap(data.heatmap);
                    setStats(data.stats);
                })
        },
        []
    )

    useEffect(
        () => {
            fetch(`${API_BASE_URL}/user/rating/${USER_HANDLE}`)
                .then(res => res.json())
                .then(data => {
                    setRatingHistory(data.rating_history)
                    setRatingStats({
                        "max_delta": data.max_delta,
                        "avg_delta": data.avg_delta,
                        "total_contest": data.total_contest
                    })
                })
        },
        []
    )

    return (
        <>
            <div className="flex w-full gap-6 p-6">
                <div className="w-1/4">
                    <UserCard
                        data={data}
                    />
                </div>
                <div className="w-3/4">
                    <SubmissionsHeatmap
                        data={heatmap}
                        stats={stats}
                    />
                </div>
            </div>
            <div className="ml-6 mr-6">
                <RatingGraph
                    data={ratingHistory}
                    stats={ratingStats}
                />
            </div>
        </>
    )
}

export default Home