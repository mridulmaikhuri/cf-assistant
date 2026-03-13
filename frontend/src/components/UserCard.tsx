interface UserCardProps {
    profilePhoto: string;
    handle: string;
    rank: string;
    rating: number;
    maxRating: number;
    maxRank: string;
}

const UserCard = ({
    profilePhoto,
    handle,
    rank,
    rating,
    maxRating,
    maxRank
}: UserCardProps) => {
    return (
        <div className="bg-gray-800 rounded-2xl shadow-xl p-8 w-105 h-110">

            {/* Profile Section */}
            <div className="flex flex-col items-center mb-6">
                <img
                    src={profilePhoto}
                    alt="Profile"
                    className="w-28 h-28 rounded-full border-4 border-gray-600 mb-4"
                />

                <h2 className="text-2xl font-semibold text-white">
                    {handle}
                </h2>

                <p className="text-gray-400 capitalize">
                    {rank}
                </p>
            </div>

            {/* Stats Section */}
            <div className="grid grid-cols-2 gap-4 text-center">

                <div className="bg-gray-700 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Rating</p>
                    <p className="text-white text-xl font-medium">
                        {rating}
                    </p>
                </div>

                <div className="bg-gray-700 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Max Rating</p>
                    <p className="text-white text-xl font-medium">
                        {maxRating}
                    </p>
                </div>

                <div className="bg-gray-700 rounded-lg p-4 col-span-2">
                    <p className="text-gray-400 text-sm">Max Rank</p>
                    <p className="text-white text-lg font-medium capitalize">
                        {maxRank}
                    </p>
                </div>

            </div>

        </div>
    );
};

export default UserCard