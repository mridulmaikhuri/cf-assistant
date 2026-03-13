import { useEffect, useState } from "react";

import { USER_HANDLE, API_BASE_URL } from "./constants/config";
import Navbar from "./components/Navbar";
import UserCard from "./components/UserCard";
import SubmissionsHeatmap from "./components/SubmissionHeatmap";

type UserData = {
    handle: string,
    profilePhoto: string,
    rating: number,
    rank: string,
    maxRating: number,
    maxRank: string,
}

type HeatmapData = {
    date: string;
    count: number;
}

type Stats = {
  max_submission: number;
  min_submission: number;
  avg_submission: number;
  max_streak: number;
  current_streak: number;
};

function App() { 
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
    min_submission: 0,
    avg_submission: 0,
    max_streak: 0,
    current_streak: 0
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

  return (
    <>
      <Navbar />
      <div className="flex w-full gap-6 p-6">
        <div className="w-1/4">
          <UserCard
            profilePhoto={data.profilePhoto}
            handle={data.handle}
            rank={data.rank}
            rating={data.rating}
            maxRating={data.maxRating}
            maxRank={data.maxRank}
          />
        </div>
        <div className="w-3/4">
          <SubmissionsHeatmap 
            data={heatmap} 
            stats={stats}
          />
        </div>
      </div>
    </>
  )
}

export default App
