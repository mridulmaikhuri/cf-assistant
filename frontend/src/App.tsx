import { useEffect, useState } from "react";

import { USER_HANDLE, API_BASE_URL } from "./constants/config";
import Navbar from "./components/Navbar";
import UserCard from "./components/UserCard";
import SubmissionsHeatmap from "./components/SubmissionHeatmap";

function App() { 
  const [data, setData] = useState<{ 
    handle: string,
    profilePhoto: string,
    rating: number,
    rank: string,
    maxRating: number,
    maxRank: string,
  }>({ 
    handle: "",
    profilePhoto: "",
    rating: 0,
    rank: "",
    maxRating: 0,
    maxRank: ""
  });

  const [heatmap, setHeatmap] = useState([]);

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
      .then(data => setHeatmap(data))
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
          />
        </div>
      </div>
    </>
  )
}

export default App
