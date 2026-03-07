import { useEffect, useState } from "react"
import {  useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import type { AppDispatch,  RootState } from "../ts/store";
import { fetchFavoriteHotel } from "../ts/authSlice";
import { formatBookingDates } from "../utils/formatBookingDates";
import api from "../ts/axiosInstance";
import type { Bookings } from "../utils/types";
import axios from "axios";
import { useNotify } from "../components/Notify";

function Profile() {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { notify } = useNotify();
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  const user = useSelector((state: RootState) => state.auth.user);
  const [page, setPage] = useState<"1" | "2" | "3">("1");
  const [render, setRender] = useState(false)
  const [bookings, setBookings] = useState<Bookings[]>([])
  const [lastBooking, setLastBooking] = useState<Bookings>()
  const favorites = useSelector((state: RootState) => state.auth.favorites)
  const [activebooking, setActiveBooking] = useState(0)
  const [finishedbooking, setFinichedBooking] = useState(0)
  const [cancelledbooking, setCancelledBooking] = useState(0)
  const fallback = "https://cf.bstatic.com/xdata/images/hotel/square600/584421551.webp?k=14f2c7c8e5bc8a3e31f34d4b8c248f88a625cea9999abe481fce0c0d5ced559b&o="
  const [lastBookingImage, setLastBookingImage] = useState(fallback);

    useEffect(() => {
        if (isAuthenticated == false) {
            navigate("/login")
        } else {
            const fetchBookings = async () => {
                try {
                    const res_last = await api.get(`/bookings?status=last`, {
                        headers: { "Content-Type": "application/json" },
                        withCredentials: true,
                    })
                    setLastBooking(res_last.data)
                    const res_all = await api.get(`/bookings?status=all`, {
                        headers: { "Content-Type": "application/json" },
                        withCredentials: true,
                    })
                    setBookings(res_all.data)
                } catch(err: unknown) {
                    if (axios.isAxiosError(err)) {
                        return notify(err.response?.data?.detail, "error")
                    } else {
                        return notify("Unknown error", "error")
                    }
                }
            }
        fetchBookings()
    }}, [isAuthenticated])

    useEffect(() => {
        if (!lastBooking?.hotel?.images?.length) return
        const main = lastBooking.hotel.images.find(img => img.is_main)?.image_url || lastBooking.hotel.images[0].image_url || fallback
        setLastBookingImage("http://localhost:80/api" + main)
    }, [lastBooking])

    useEffect(() => {
        let count_active = 0
        let count_finished = 0
        let count_cancelled = 0
        bookings?.forEach((booking) => {
            if (booking.status == "confirmed") count_active++
            if (booking.status == "completed") count_finished++
            if (booking.status == "cancelled") count_cancelled++
        })
        setActiveBooking(count_active)
        setFinichedBooking(count_finished)
        setCancelledBooking(count_cancelled)
    }, [bookings])

    useEffect(() => {
        if (page == "1") setRender(false)
        if (page == "3") {
            dispatch(fetchFavoriteHotel())
            setRender(true)
        }
    }, [page])

    const handelCancelBooking = async (id: number) => {
        try {
            const res = await api.post(`/bookings/${id}/cancel`)
            setBookings(prev => prev?.map( s =>s.id === id ? { ...s, status: "cancelled" } : s ))
            return res.data
        } catch(err: unknown) {
            if (axios.isAxiosError(err)) {
                return notify(err.response?.data?.detail, "error")
            } else {
                return notify("Unknown error", "error")
            }
        }
    }

    return(
        <>
          <div className="max-w-7xl mx-auto px-6 pb-20">
            <div className="grid grid-cols-4 gap-6">
                <aside className="lg:col-span-1">
                    <div className="bg-white/4 p-6 rounded-2xl shadow-lg">
                        <div className="flex gap-4 items-center mb-6">
                            <div className="bg-white rounded-full w-14 h-14"></div>
                            <div>
                                <div className="font-semibold">{user?.username}</div>
                                <div className="text-sm text-white/70">{user?.email}</div>
                            </div>
                        </div>
                        <nav className="space-y-1 text-sm">
                            <button className="py-2 w-full px-3 text-left rounded-md bg-white/8" onClick={() => setPage("1")}>Overview</button>
                            <button className="py-2 w-full px-3 text-left rounded-md" onClick={() => setPage("2")}>My Bookings</button>
                            <button className="py-2 w-full px-3 text-left rounded-md" onClick={() => setPage("3")}>Favorite Hotels</button>
                        </nav>
                    </div>
                </aside>
                <section className="lg:col-span-3">
                    
                    { page == "1" && 
                        <div>
                            <div className="grid grid-cols-3 gap-4 mb-6 mt-5">
                                <div className="bg-white/4 p-5 rounded-2xl">
                                    <div className="text-sm mb-1 text-white/70">Active Bookings</div>
                                    <div className="font-bold text-3xl">{activebooking}</div>
                                </div>
                                <div className="bg-white/4 p-5 rounded-2xl">
                                    <div className="text-sm mb-1 text-white/70">Completed Trips</div>
                                    <div className="font-bold text-3xl">{finishedbooking}</div>
                                </div>
                                <div className="bg-white/4 p-5 rounded-2xl">
                                    <div className="text-sm mb-1 text-white/70">Cancelled Trips</div>
                                    <div className="font-bold text-3xl">{cancelledbooking}</div>
                                </div>
                            </div>
                            <div className="bg-white/4 p-6 rounded-2xl">
                                <h3 className="mb-3 font-semibold text-lg">Upcoming Trip</h3>
                                {lastBooking && (
                                    <div className="flex items-center p-4 bg-white/5 rounded-xl mt-4">
                                        <img src={lastBookingImage} className="w-24 h-16 rounded-md object-cover"/>
                                        <div className="flex-1 ml-4">
                                            <div className="font-semibold">{lastBooking?.hotel.name}</div>
                                            <p className="text-sm text-white/70">{formatBookingDates(lastBooking?.date_from, lastBooking?.date_to)} • {lastBooking?.room.capacity} guest</p>
                                        </div>
                                        <button className="rounded-md bg-blue-500/20 hover:bg-blue-500/40 py-2 px-4 transition" onClick={() => navigate(`/hotels/${lastBooking?.hotel.id}`)}>View</button>
                                    </div>
                                )}
                            </div>
                        </div>
                    }
                    { page == "2" &&
                        <div>
                            <div className="bg-white/4 p-6 rounded-2xl mt-5">
                                <h3 className="mb-3 font-semibold text-lg">All Bookings</h3>
                                {bookings?.map(booking => {
                                const mainImage = booking.hotel?.images?.find(img => img.is_main)?.image_url  || booking.hotel?.images?.[0]?.image_url  || fallback;

                                    return (
                                        <div className="flex items-center p-4 bg-white/5 rounded-xl mt-4" key={booking.id}>
                                            <img src={"http://localhost:80/api" + mainImage} alt="" className="w-24 h-16 rounded-md object-cover"/>
                                            <div className="flex-1 ml-4">
                                                <div className="font-semibold">{booking?.hotel.name}</div>
                                                <p className="text-sm text-white/70">{formatBookingDates(booking.date_from, booking.date_to)} • {booking.room.capacity} guest</p>
                                                <p className="text-sm text-indigo-300">Status: {booking.status == "pending" && "Pending"} {booking.status == "confirmed" && "Confirmed"} {booking.status == "cancelled" && "Cancelled"} {booking.status == "completed" && "Completed"}</p>
                                            </div>
                                            <div className="flex">
                                                {booking.status == "pending" ? <button className="rounded-md bg-blue-500/20 hover:bg-blue-500/40 py-2 px-4 transition" onClick={() => navigate("/booking/pay", {state: { id: booking.id, total_price: booking.total_price, name_hotel: booking.hotel.name, name_room: booking.room.name, date_from: booking.date_from, date_to: booking.date_to, guests: booking.room.capacity }})}>Pay</button> : <button className="rounded-md bg-blue-500/20 hover:bg-blue-500/40 py-2 px-4 transition" onClick={() => navigate(`/hotels/${booking?.hotel.id}`)}>View</button>}
                                                {booking.status == "pending" || booking.status == "confirmed" ? (
                                                    <button className="ml-4 px-3 py-1 rounded-md border border-white/10 bg-white/5 hover:bg-white/10 transition" onClick={() => handelCancelBooking(booking.id)}>Cancel</button>
                                                ) : null }                                          
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    }
                    { (page == "3" && favorites && render == true) &&
                        <div>
                            <div className="bg-white/4 p-6 rounded-2xl mt-5">
                                <h3 className="mb-3 font-semibold text-lg">Favorite Hotels</h3>
                                <div className="grid grid-cols-2 gap-3">
                                {favorites?.map(favorite => {
                                    const mainImage = favorite.hotel?.images?.find(img => img.is_main)?.image_url || favorite.hotel?.images?.[0]?.image_url || fallback;

                                    return (
                                        <div className="flex p-4 bg-white/5 rounded-xl mt-4" key={favorite.id}>
                                            <img src={"http://localhost:80/api" + mainImage} alt="" className="w-24 h-16 rounded-md object-cover"/>
                                            <div className="flex-1 ml-4">
                                                <div className="font-semibold hover:underline" onClick={() => navigate(`/hotels/${favorite.hotel_id}`)}>{favorite.hotel.name}</div>
                                                <p className="text-sm text-white/70">from: ${favorite.hotel.price_per_night}</p>
                                            </div>
                                        </div>
                                    )
                                })}
                                </div>
                            </div>
                        </div>
                    }
                </section>
            </div>
          </div>
        </>
    )
}

export default Profile