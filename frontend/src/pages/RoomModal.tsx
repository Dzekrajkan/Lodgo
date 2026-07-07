import { useState } from "react"
import type { Room } from "../ts/types"
import { formatBookingDates } from "../utils/formatBookingDates"
import { Calendar, User } from "lucide-react"

const imageHostUrl = import.meta.env.VITE_IMAGE_HOST_URL
const FALLBACK = "https://img.freepik.com/free-photo/luxury-villa-with-infinity-pool-sunset-coastal-view_23-2151986080.jpg?w=400&q=80"

interface RoomModalProps {
    room: Room
    dateFrom: string
    dateTo: string
    onClose: () => void
    onBook: (room: Room) => void
}

function RoomModal({ room, dateFrom, dateTo, onClose, onBook }: RoomModalProps) {
    const [currentImg, setCurrentImg] = useState(0)
    const nights = Math.ceil((new Date(dateTo).getTime() - new Date(dateFrom).getTime()) / (1000 * 60 * 60 * 24))
    const total = room.price_per_night * nights
    const images = room.images?.length ? room.images.map(img => `http://${imageHostUrl}/api${img.image_url}`) : [FALLBACK]
    const prev = () => setCurrentImg(i => (i === 0 ? images.length - 1 : i - 1))
    const next = () => setCurrentImg(i => (i === images.length - 1 ? 0 : i + 1))

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-[#111316] border border-white/10 rounded-2xl w-[560px] overflow-hidden shadow-2xl" onClick={(e) => e.stopPropagation()}>
                <div className="flex h-[220px]">
                    <div className="relative w-[260px] shrink-0 bg-white/5 overflow-hidden">
                        <img src={images[currentImg]} alt={room.name} className="w-full h-full object-cover opacity-85"/>

                        <button
                            className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 transition rounded-full w-7 h-7 flex items-center justify-center text-white text-sm"
                            onClick={prev}
                        >‹</button>
                        <button
                            className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 transition rounded-full w-7 h-7 flex items-center justify-center text-white text-sm"
                            onClick={next}
                        >›</button>

                        <div className="absolute bottom-2.5 left-1/2 -translate-x-1/2 flex gap-1.5">
                            {images.map((_, i) => (
                                <button key={i} className={`h-[3px] rounded-full transition-all ${i === currentImg ? "w-5 bg-white" : "w-5 bg-white/30"}`} onClick={() => setCurrentImg(i)}/>
                            ))}
                        </div>
                    </div>

                    <div className="p-[18px_20px] flex-1 flex flex-col justify-between">
                        <div>
                            <div className="flex justify-between items-start mb-2">
                                <h2 className="text-base font-medium leading-snug">{room.name}</h2>
                                <button className="text-white/40 hover:text-white transition text-base leading-none ml-3" onClick={onClose}>✕</button>
                            </div>
                            <p className="text-[13px] text-white/60 leading-relaxed line-clamp-3">{room.description}</p>
                        </div>

                        <div className="grid grid-cols-3 gap-2">
                            <div className="bg-white/5 rounded-lg p-2 text-center">
                                <div className="text-[11px] text-white/40 mb-0.5">Price/night</div>
                                <div className="text-[15px] font-medium text-green-400">${room.price_per_night}</div>
                            </div>
                            <div className="bg-white/5 rounded-lg p-2 text-center">
                                <div className="text-[11px] text-white/40 mb-0.5">Guests</div>
                                <div className="text-[15px] font-medium flex items-center justify-center">{room.capacity} <User size={16} /></div>
                            </div>
                            <div className="bg-white/5 rounded-lg p-2 text-center">
                                <div className="text-[11px] text-white/40 mb-0.5">Available</div>
                                <div className={`text-[15px] font-medium ${room.available > 0 ? "text-green-400" : "text-red-400"}`}>
                                    {room.available > 0 ? `${room.available} left` : "Sold out"}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="px-5 py-3.5 border-t border-white/8 flex items-center gap-3">
                    <div className="flex-1 text-[12px] text-white/40">
                        {nights > 0
                            ? <div className="flex items-center"><Calendar size={16} className="mr-1" />{formatBookingDates(dateFrom, dateTo)} · {nights} nights · <span className="text-white/60">Total ${total}</span></div>
                            : <span>Select dates to see total</span>
                        }
                    </div>
                    <button className="py-1.5 px-4 rounded-lg border border-white/10 text-white/60 hover:bg-white/5 transition text-[13px]" onClick={onClose}>Close</button>
                    <button
                        className="py-1.5 px-5 rounded-lg bg-blue-500/20 hover:bg-blue-500/40 text-blue-300 transition text-[13px] font-medium disabled:opacity-40 disabled:cursor-not-allowed"
                        onClick={() => { onBook(room); onClose() }}
                        disabled={room.available === 0}
                    >Book now</button>
                </div>
            </div>
        </div>
    )
}

export default RoomModal