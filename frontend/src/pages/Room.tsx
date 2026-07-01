interface RoomInterface {
  id: number
  hotel_id: number
  name: string
  description: string
  price_per_night: number
  quantity: number
  capacity: number
}

interface RoomModalProps {
  room: RoomInterface
  onClose: () => void
}

function RoomModal({ room, onClose }: RoomModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl p-6 w-[400px] text-gray-600" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-xl font-semibold mb-2">{room.name}</h2>
        <p className="mb-3">{room.description}</p>
        <p className="font-medium">Price: $ {room.price_per_night}</p>
        <button onClick={onClose} className="mt-4 text-sm underline">Close</button>
      </div>
    </div>
  )
}

export default RoomModal
