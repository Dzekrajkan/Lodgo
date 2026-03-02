import React, { useEffect, useState } from "react"
import { useDispatch, useSelector } from "react-redux"
import { useNavigate, useParams } from "react-router-dom"
import type { AppDispatch, RootState } from "../ts/store"
import Room from "./Room"
import type { Hotel as HotelType, Room as RoomType } from "../utils/types"
import { setFavorites } from "../ts/authSlice"
import api from "../ts/axiosInstance"
import { useNotify } from "../components/Notify"
import axios from "axios"

interface User {
    id: number,
    username: string
}

interface Reviews {
    id: number,
    user_id: number,
    hotel_id: number,
    booking_id: number | null,
    rating: number,
    comment: string,
    create_at: string
    user: User
}

function Hotel() {
    const { hotelId } = useParams()
    const navigate = useNavigate()
    const dispatch = useDispatch<AppDispatch>()
    const { notify } = useNotify()
    const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
    const [hotel, setHotel] = useState<HotelType>()
    const [rooms, setRooms] = useState<RoomType[]>([])
    const favorites = useSelector((state: RootState) => state.auth.favorites)
    const isFavorite = hotel ? favorites?.some(favorite => favorite.hotel_id === hotel.id) : false
    const [reviews, setReviews] = useState<Reviews[] | null>(null)
    const [rating, setRating] = useState(0)
    const [comment, setComment] = useState("")
    const [mainImage, setMainImage] = useState<string | null>(null)
    const [image, setImage] = useState<string | null>(null)
    const [hotel_id, setHotelId] = useState(0)
    const [date_from, setDate_from] = useState("")
    const [date_to, setDate_to] = useState("")
    const [guests, setGuests] = useState(1)
    const [filterRoom, setFilterRoom] = useState(false)
    const [selectedRoom, setSelectedRoom] = useState<RoomType | null>(null)
    const [visibleCount, setVisibleCount] = useState(1)
    const fallback = "https://cf.bstatic.com/xdata/images/hotel/square600/584421551.webp?k=14f2c7c8e5bc8a3e31f34d4b8c248f88a625cea9999abe481fce0c0d5ced559b&o="
    const scrollToReviewForm = () => {
        const form = document.getElementById("review-form")
        if (form) {
            form.scrollIntoView({ behavior: "smooth", block: "center" })
        }
    }
    
    useEffect(() => {
        if (hotelId) {
            setHotelId(Number(hotelId))
            const fetchReviews = async () => {
                try {
                    const res_reviews = await api.get(`/reviews/${hotelId}`)
                    const res_hotel = await api.get(`/hotels/${hotelId}`)
                    setReviews(res_reviews.data)
                    setHotel(res_hotel.data)
                } catch (err: unknown) {
                    if (axios.isAxiosError(err)) {
                        return notify(err.response?.data?.detail, "error")
                    } else {
                        return notify("Unknown error", "error")
                    }
                }
            }
            fetchReviews()
        }
    }, [hotelId])

    useEffect(() => {
        if (!hotel?.images?.length) return

        const main = (hotel.images.find(img => img.is_main)?.image_url || hotel.images[0]?.image_url)
        setMainImage("http://127.0.0.1:8002" + main)
    }, [hotel])

    if (!hotel) {
        return <div className="flex items-center justify-center">Loading...</div>
    }

    const handelfilter = async(e: React.FormEvent) => {
      e.preventDefault();

      if (date_from.length <= 0) return notify("Enter your arrival date", "msg");
      if (date_to.length <= 0) return notify("Enter your departure date", "msg");

      try {
        const res = await api.get(`/hotels/${hotel_id}/rooms?&date_from=${date_from}&date_to=${date_to}&guests=${guests}`)
        setRooms(res.data)
      } catch (err: unknown) {
        if (axios.isAxiosError(err)) {
            return notify(err.response?.data?.datail || "Error loading numbers", "error")
        } else {
            return notify("Unknown error", "error")
        }
      }
      setFilterRoom(true)
    }

    const handelCreateBooking = async(room: RoomType) => {
        if (!isAuthenticated) return notify("Please sign in to continue.", "msg")
        if (date_from.length <= 0) return notify("Enter your arrival date", "msg");
        if (date_to.length <= 0) return notify("Enter your departure date", "msg");
        navigate("/booking", {
            state: {
                room,
                hotel: hotel,
                main_image: mainImage,
                date_from: date_from,
                date_to: date_to,
                guests: guests
            }
        })
    }

    const handelAddFavorite = async() => {
        try {
            const res = await api.post(`/favorite?status=add`, {
                hotel_id: hotel.id,
                headers: { "Content-Type": "application/json" },
                withCredentials: true,
            })
            dispatch(setFavorites([...(favorites || []), res.data]))
        } catch(err: unknown) {
            if (axios.isAxiosError(err)) {
                return notify(err.response?.data?.detail, "error")
            } else {
                return notify("Unknown error", "error")
            }
        }
    }

    const handelRemoveFavorite = async() => {
        try {
            await api.post(`/favorite?status=remove`, {
                hotel_id: hotel.id,
                headers: { "Content-Type": "application/json" },
                withCredentials: true,
            })
            dispatch(setFavorites(favorites?.filter(f => f.hotel_id !== hotel.id)))
        } catch(err: unknown) {
            if (axios.isAxiosError(err)) {
                return notify(err.response?.data?.detail, "error")
            } else {
                return notify("Unknown error", "error")
            }
        }
    }

    const handelCreateReview = async(e: React.FormEvent) => {
        e.preventDefault()
        try {
            if (rating <= 0) return notify("Rate this review", "msg")
            if (comment.length <= 0) return notify("Write a review text")
            await api.post("/review", {hotel_id: hotelId, booking_id: null, rating: rating, comment: comment,
                headers: { "Content-Type": "application/json" },
                withCredentials: true,
            })
        } catch(err: unknown) {
            if (axios.isAxiosError(err)) {
                return notify(err.response?.data?.detail, "error")
            } else {
                return notify("Unknown error", "error")
            }
        }
    }

    const handleLoadMoreReviews = () => {
        setVisibleCount(prev => prev + 5)
    }

    const handleShareHotel = async () => {
        try {
            await navigator.clipboard.writeText(window.location.href)
            notify("The hotel link has been copied", "msg")
        } catch {
            notify("Failed to copy hotel link", "error")
        }
    }

    return (
        <>
          <div className="max-w-7xl mx-auto px-6 pb-20">
            <div className="flex justify-between items-end">
              <div className="flex flex-col">
                  <h1 className="text-4xl font-bold mb-2">{hotel.name}</h1>
                  <p className="text-sm text-white/70 mb-4">{hotel.address}</p>
                  <div className="flex items-center gap-1">
                    <div className="py-3 px-1 text-sm">{hotel.rating}★</div>
                    <div className="text-sm text-white/70">• {hotel.reviews_count} отзыва</div>
                  </div>
              </div>
              <div className="inline-flex items-center gap-3">
                <button className="px-4 py-2 rounded-md border border-white/10 bg-white/4" onClick={handleShareHotel}>Share</button>
                {isFavorite ? <button className="px-4 py-2 rounded-md bg-red-500/20 hover:bg-red-500/40 transition" onClick={handelRemoveFavorite}>Remove from Favorites</button> : <button className="px-4 py-2 rounded-md bg-blue-500/20 hover:bg-blue-500/40 transition" onClick={handelAddFavorite}>Add to Favorites</button>}
              </div>
            </div>
            <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="col-span-2 space-y-5">
                    <div className="rounded-2xl overflow-hidden shadow-lg bg-white/5">
                        <div className="w-full h-72 md:h-96 relative">
                            {mainImage && <img src={image || mainImage || fallback} className="w-full h-full object-fill"/>}
                        </div>
                        <div className="p-4 flex gap-3 overflow-x-auto">
                            {hotel.images.map(image => (
                                <img src={"http://127.0.0.1:8002" + image.image_url} onClick={() => setImage("http://127.0.0.1:8002" + image.image_url)}  key={image.id} className="cursor-pointer ring-1 ring-white/6 w-26 h-20 object-cover rounded-lg"/>
                            ))}
                        </div>
                    </div>
                    <div>
                        <div className="bg-white/4 p-6 rounded-2xl shadow-lg">
                            <h3 className="font-semibold text-lg mb-3">Description</h3>
                            <p className="mt-3 text-sm text-white/80">{hotel.description}</p>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-8">
                        <div className="bg-white/4 p-6 rounded-2xl shadow-lg">
                            <h3 className="font-semibold text-lg mb-3">Facilities</h3>
                            <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-white/80">
                                {hotel.facilities.map(facilities => 
                                    <div key={facilities.id}>{facilities.name}</div>
                                )}
                            </div>
                        </div>
                        <div className="bg-white/4 p-6 rounded-2xl shadow-lg">
                            <h3 className="font-semibold text-lg mb-3">Rules & Policy</h3>
                            <div className="mt-3 text-sm text-white/80">
                                <div className="mb-2"><strong>Check-in:</strong> from {hotel.check_in_time}</div>
                                <div className="mb-2"><strong>Check-out:</strong> until {hotel.check_out_time}</div>
                                <div className="mb-2"><strong>Cancellation:</strong> Free up to 48 hours before arrival</div>
                                <div className="mb-2"><strong>Payment:</strong> Cash or card on site</div>
                            </div>
                        </div>
                    </div>
                    <div>
                        <div className="bg-white/4 p-6 rounded-2xl shadow-lg">
                            <h3 className="font-semibold text-lg mb-3">Availability</h3>
                            <div className="grid grid-cols-10 gap-1 text-center text-sm">
                                <h3 className="py-4 bg-white/5 col-span-3">Room Type</h3>
                                <h3 className="py-4 bg-white/5 col-span-2">Guests</h3>
                                <h3 className="py-4 bg-white/5 col-span-2">Today's Price</h3>
                                <h3 className="py-4 bg-white/5 col-span-3"></h3>
                            </div>
                            <ul>
                                {filterRoom == true && rooms.map(room => 
                                    <div className="grid grid-cols-10 gap-1 mt-1" key={room.id}>
                                        <div className="col-span-3 p-2 bg-white/8">
                                            <a className="font-semibold underline cursor-pointer" onClick={() => setSelectedRoom(room)}>{room.name}</a>
                                            <p className="text-sm text-white/80">{room.description}</p>
                                        </div>
                                        <div className="col-span-2 p-2 bg-white/8">
                                            <h3>{room.capacity}</h3>
                                        </div>
                                        <div className="col-span-2 p-2 bg-white/8">
                                            <h3 className="text-lg font-bold">${room.price_per_night}</h3>
                                        </div>
                                        <div className="col-span-3 p-2 items-center flex justify-center bg-white/8">
                                            <button className="rounded-md bg-blue-500/20 hover:bg-blue-500/40 py-2 px-10 transition" onClick={() => handelCreateBooking(room)}>Book Now</button>
                                        </div>
                                    </div>
                                 )}
                            </ul>
                            {selectedRoom && (<Room room={selectedRoom} onClose={() => setSelectedRoom(null)} />)}
                            <div className="border-t border-white/8 flex border-2"></div>
                        </div>
                    </div>
                    <div className="col-span-2">
                        <div className="bg-white/5 p-6 rounded-2xl shadow-lg sticky top-6 space-y-6">
                            <div className="flex justify-between">
                                <div>
                                    <h3 className="text-3xl font-bold">{hotel.rating}</h3>
                                    <p className="text-sm text-white/70">Number of reviews - {hotel.reviews_count}</p>
                                </div>
                                <div className="flex items-center">
                                    <button className="px-4 py-2 rounded-md border border-white/10" onClick={scrollToReviewForm}>Write a Review</button>
                                </div>
                            </div>
                            <div className="flex flex-col gap-3">
                                {reviews?.slice(0, visibleCount).map(review => (
                                    <div className="bg-white/5 p-6 rounded-2xl shadow-lg" key={review.id}>
                                        <div className="flex items-start gap-3">
                                            <div className="bg-white rounded-full w-10 h-10 items-center justify-center flex text-black">M</div>
                                            <div className="flex-1">
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <h3 className="font-semibold">{review.user.username}</h3>
                                                        <p className="text-xs text-white/70">{review.create_at}</p>
                                                    </div>
                                                    <div>
                                                        <div className="font-semibold">{review.rating}</div>
                                                    </div>
                                                </div>
                                                <p className="mt-2 text-sm text-white/80">{review.comment}</p>
                                            </div>
                                        </div> 
                                    </div>
                                ))}
                            </div>
                            <div className="flex items-center justify-center">
                                {reviews && visibleCount < reviews.length && (
                                    <button className="px-4 py-2 rounded-md border border-white/10" onClick={handleLoadMoreReviews}>Load More</button>
                                )}
                            </div>
                            <div className="border-t pt-6">
                                <h3 className="mb-4">Leave a Review</h3>
                                <form onSubmit={(e) => handelCreateReview(e)} id="review-form">
                                    <div className="flex items-center mb-4 ml-4">
                                        <p className="text-sm text-white/80 mr-3">Rating</p>
                                        <div className="flex gap-1">
                                            <button type="button" className={`text-xl ${rating >= 1 ? "text-yellow-400" : "text-white/30"}`} onClick={() => setRating(1)}>★</button>
                                            <button type="button" className={`text-xl ${rating >= 2 ? "text-yellow-400" : "text-white/30"}`} onClick={() => setRating(2)}>★</button>
                                            <button type="button" className={`text-xl ${rating >= 3 ? "text-yellow-400" : "text-white/30"}`} onClick={() => setRating(3)}>★</button>
                                            <button type="button" className={`text-xl ${rating >= 4 ? "text-yellow-400" : "text-white/30"}`} onClick={() => setRating(4)}>★</button>
                                            <button type="button" className={`text-xl ${rating >= 5 ? "text-yellow-400" : "text-white/30"}`} onClick={() => setRating(5)}>★</button>
                                        </div>
                                    </div>
                                    <textarea className="w-full rounded-md border border-white/10 bg-transparent py-2 px-3 mb-2" placeholder="Share your experience" value={comment} onChange={(e) => setComment(e.target.value)}></textarea>
                                    <div className="flex gap-4">
                                        <button className="px-6 py-2 rounded-md bg-blue-500/20 hover:bg-blue-500/40 transition" type="submit">Send</button>
                                        <button className="px-4 py-2 rounded-md border border-white/10" type="button" onClick={() => {setComment(""), setRating(0)}}>Clean out</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-span-1">
                    <div className="bg-white/5 p-6 rounded-2xl shadow-lg sticky top-6">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="text-2xl font-bold">from ${hotel.price_per_night}</div>
                            <div className="text-sm text-white/70">/ night</div>
                        </div>
                        <form onSubmit={handelfilter}>
                            <div>
                                <label htmlFor="" className="text-sm text-gray-300">Check-in Date</label>
                                <input type="date" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent mt-1" value={date_from} onChange={(e) => setDate_from(e.target.value)}/>
                            </div>
                            <div>
                                <label htmlFor="" className="text-sm text-gray-300">Check-out Date</label>
                                <input type="date" lang="en" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent mt-1" value={date_to} onChange={(e) => setDate_to(e.target.value)}/>
                            </div>
                            <div className="mt-2">
                                <label htmlFor="" className="text-sm text-gray-300">Guests</label>
                                <div className="flex gap-2 mt-1">
                                    <select className="py-2 px-2 border border-white/10 rounded-md w-full" value={guests} onChange={(e) => setGuests(Number(e.target.value))}>
                                        <option className="text-black" value={1}>1 adult</option>
                                        <option className="text-black" value={2}>2 adults</option>
                                        <option className="text-black" value={4}>Family — 2 adults, 2 children</option>
                                    </select>
                                </div>
                            </div>
                            <div>
                                <button type="submit" className="w-full py-2 mt-4 rounded-md bg-blue-500/20 hover:bg-blue-500/40 transition">Room search</button>
                            </div>
                        </form>
                        <div className="mt-4 text-sm text-white/70">
                            <div>
                                <strong>Free Cancellation </strong> 
                                up to 48 hours before arrival
                            </div>
                            <div className="mt-5">
                                Need help?
                                <a href="#" className="underline ml-1">Contact Us</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </>
    )
}

export default Hotel