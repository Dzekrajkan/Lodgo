interface AvatarProps {
  username: string;
  size?: number
}

export const Avatar = ({ username, size=10 }: AvatarProps) => {
    return (
        <div className={`bg-white rounded-full w-${size} h-${size} items-center justify-center flex text-black font-semibold`}>{username[0].toUpperCase()}</div>
    )
}