import { useSelector } from "react-redux"
import type { RootState } from "../ts/store"
import { useState } from "react"
import { useLocation, useNavigate } from "react-router-dom"
import api from "../ts/axiosInstance"
import type { Hotel, Room, Services } from "../utils/types"
import { useNotify } from "../components/Notify"

function CreateBooking() {
    const navigate = useNavigate()
    const { notify } = useNotify()
    const location = useLocation()
    const user = useSelector((state: RootState) => state.auth.user)
    const [firstName, setFirstName] = useState("")
    const [lastName, setLastName] = useState("")
    const [email, setEmail] = useState("")
    const [useAccountData, setUseAccountData] = useState(false)
    const {room, hotel, main_image, date_from, date_to, guests} = location.state as {
        room: Room,
        hotel: Hotel,
        main_image: string,
        date_from: string,
        date_to: string,
        guests: number
    }
    const [selectedServices, setSelectedServices] = useState<Services[]>([])
    const servicesTotal = selectedServices.reduce((sum, service) => sum + service.price, 0)
    const nights = Math.ceil((new Date(date_to).getTime() - new Date(date_from).getTime()) / (1000 * 60 * 60 * 24))
    const totalPrice = room.price_per_night * nights + servicesTotal

    const handelGetDataAccount = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const checked = e.target.checked
        setUseAccountData(checked)

        if (checked) {
            const [fName, lName] = user?.username.split(" ") || ["", ""]
            setFirstName(fName)
            setLastName(lName)
            setEmail(String(user?.email))
        } else {
            setFirstName("")
            setLastName("")
            setEmail("")
        }
    }

    const toggleService = (service: Services) => {
        setSelectedServices(prev => {
            const exists = prev.find(s => s.id === service.id)

            if (exists) {
                return prev.filter(s => s.id !== service.id)
            } else {
                return [...prev, service]
            }
        })
    }

    const handelCreateBooking = async () => {
        try {
            const res = await api.post(`/bookings`, { 
                hotel_id: hotel.id, room_id: room.id, date_from: date_from, date_to: date_to, guest_first_name: firstName, guest_last_name: lastName, guest_email: email, service_ids: selectedServices.map(s => s.id),
                headers: { "Content-Type": "application/json" },
                withCredentials: true,
            });
            const data = res.data
            navigate("/booking/pay", {
                state: {
                    id: data.id,
                    total_price: data.total_price,
                    name_hotel: hotel.name,
                    name_room: room.name,
                    date_from: date_from,
                    date_to: date_to,
                    guests: room.capacity
                }
            })
        } catch(err: any) {
            return notify(err, "error")
        }
    }

    return (
        <>
          <main className="max-w-7xl mx-auto px-6 pb-20 grid grid-cols-1 lg:grid-cols-3 gap-6">
            <section className="lg:col-span-2 space-y-6">
                <div className="p-6 rounded-2xl bg-white/4">
                    <div className="flex justify-between">
                        <h3 className="text-lg font-semibold">Guest Information</h3>
                        <div className="flex items-center">
                            <div>
                                <input type="checkbox" checked={useAccountData} onChange={handelGetDataAccount}/>
                            </div>
                            <span className="text-xs text-white/80 group-hover:text-white transition">Use my account data</span>
                        </div>
                    </div>
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input type="text" placeholder="First Name" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={firstName} onChange={(e) => setFirstName(e.target.value)}/>
                        <input type="text" placeholder="Last Name" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={lastName} onChange={(e) => setLastName(e.target.value)}/>
                        <input type="email" placeholder="Email" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent md:col-span-2" value={email} onChange={(e) => setEmail(e.target.value)}/>
                    </div>
                </div>
                <div className="p-6 rounded-2xl bg-white/4">
                    <div>
                        <h3 className="text-lg font-semibold">Stay Details</h3>
                    </div>
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="text-sm text-gray-300">Check-in Date</label>
                            <input type="date" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={String(date_from)} readOnly/>
                        </div>
                        <div>
                            <label className="text-sm text-gray-300">Check-out Date</label>
                            <input type="date" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={String(date_to)} readOnly/>
                        </div>
                        <div>
                            <label className="text-sm text-gray-300">Guests</label>
                            <select className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" defaultValue={Number(guests)}>
                                <option className="text-black" value={1}>1 adult</option>
                                <option className="text-black" value={2}>2 adults</option>
                                <option className="text-black" value={4}>Family — 2 adults, 2 children</option>
                            </select>
                        </div>
                    </div>
                </div>
                {hotel.services.length > 0 && (
                    <div className="p-6 rounded-2xl bg-white/4">
                        <div>
                            <h3 className="text-lg font-semibold mb-4">Additional Services</h3>
                        </div>
                        <div className="flex flex-col space-y-2">
                            {hotel.services.map(service => 
                                <div className="flex gap-2" key={service.id}>
                                    <input type="checkbox" onChange={() => toggleService(service)}/>
                                    <label htmlFor="">{service.name} (+${service.price})</label>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </section>

            <aside className="space-y-6">
                <div className="p-6 rounded-2xl bg-white/4">
                    <h3 className="font-semibold mb-3">Your Booking</h3>
                    <div className="flex mb-4">
                        <img src={main_image} alt="" className="w-32 h-16 rounded-md object-cover"/>
                        <div className="items-center ml-3">
                            <h3 className="font-semibold">{hotel.name}</h3>
                            <p className="text-sm text-white/70">{room.name}</p>
                        </div>
                    </div>
                    <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                            <span>Nights</span>
                            <span>{nights}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Price per night</span>
                            <span>${room.price_per_night}</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Extra services</span>
                            <span>${servicesTotal}</span>
                        </div>
                        <div className="border-t border-white/10 pt-2 flex justify-between font-semibold text-lg">
                            <span>Total</span>
                            <span>${totalPrice}</span>
                        </div>
                    </div>
                </div>
                <div className="p-6 rounded-2xl bg-white/4">
                    <button className="w-full py-3 rounded-md bg-blue-500/20 hover:bg-blue-500/40 transition" onClick={handelCreateBooking}>Proceed to Payment</button>
                </div>
            </aside>

          </main>
        </>
    )
}

export default CreateBooking