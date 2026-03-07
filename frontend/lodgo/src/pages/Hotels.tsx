import { useLocation, useNavigate } from "react-router-dom";
import React, { useEffect, useState } from "react";
import type { Hotel, Facilities } from "../utils/types";
import api from "../ts/axiosInstance";
import { useNotify } from "../components/Notify";
import axios from "axios";

function Hotels() {
    const navigate = useNavigate();
    const { notify } = useNotify()
    const location = useLocation();
    const [hotels, setHotels] = useState<Hotel[]>([])
    const [allHotels, setAllHotels] = useState<Hotel[]>([])
    const [city, setCity] = useState("")
    const [date_from, setDate_from] = useState("")
    const [date_to, setDate_to] = useState("")
    const [guests, setGuests] = useState(1)
    const [facilities, setFacilities] = useState<Facilities[]>([])
    const [activeFacilities, setActiveFacilities] = useState<number[]>([])
    const [stars, setStars] = useState(0)
    const [autoSearch, setAutoSearch] = useState(false)
    const state = location.state as any || {}
    const {city_u, date_from_u, date_to_u, guests_u} = state as {
      city_u: string | null,
      date_from_u: string | null,
      date_to_u: string | null,
      guests_u: number | null
    }
    const [activeFilter, setActiveFilter] = useState(false)
    const hotelsToRender = activeFilter ? hotels : allHotels

    useEffect(() => {
      const fetch = async () => {
        try {
          const res_facilities = await api.get("/facilities")
          setFacilities(res_facilities.data)

          if (city_u && date_from_u && date_to_u && guests_u) {
            setCity(city_u)
            setDate_from(date_from_u)
            setDate_to(date_to_u)
            setGuests(guests_u)
            setAutoSearch(true)
          } else {
            const res_hotel = await api.get("/hotels")
            setAllHotels(res_hotel.data)
          }
        } catch(err: unknown) {
            if (axios.isAxiosError(err)) {
              return notify(err.response?.data?.detail, "error")
            } else {
              return notify("Unknown error", "error")
            }
        }
    }

      fetch()
    }, [])

    useEffect(() => {
      if (autoSearch  && city && date_from && date_to && guests) {
        handelsearch(null)
        setAutoSearch(false)

        navigate(location.pathname, {
          replace: true,
          state: null
        })
      }
    }, [autoSearch, city, date_from, date_to, guests])

    const handelsearch = async(e: React.FormEvent | null) => {
      if (e) e.preventDefault();

      if (city.length <= 0) return notify("Enter city", "msg");
      if (date_from.length <= 0) return notify("Enter your arrival date", "msg");
      if (date_to.length <= 0) return notify("Enter your departure date", "msg");

      try {
        const res = await api.get(`/hotels/search?city=${city}&date_from=${date_from}&date_to=${date_to}&guests=${guests}`)
        setAllHotels(res.data)
      } catch(err: unknown) {
          if (axios.isAxiosError(err)) {
            return notify(err.response?.data?.detail, "error")
          } else {
            return notify("Unknown error", "error")
          }
        }
    }

    const addFacilities = async (id: number) => {
      setActiveFacilities(prev => prev.includes(id) ? prev.filter(af => af !== id) : [...prev, id])
    }

    const handelfilter = async(e: React.FormEvent) => {
      e.preventDefault()
      
      let filtered = [...allHotels]

      if (stars > 0) {
        filtered = filtered.filter(hotel => hotel.rating >= Number(stars))
      }

      if (activeFacilities.length > 0) {
        filtered = filtered.filter(hotel => activeFacilities.every(f => hotel.facilities.some(hf => hf.id === f)))
      }

      setActiveFilter(true)
      setHotels(filtered)
    }

    const handleClearShearch = async () => {
      if (city.length <= 0) return notify("Enter city", "msg");
      if (date_from.length <= 0) return notify("Enter your arrival date", "msg");
      if (date_to.length <= 0) return notify("Enter your departure date", "msg");
      try {
        const res = await api.get("/hotels")
        setAllHotels(res.data)
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
            <div className="mt-6 glass rounded-2xl px-6 py-4 shadow-lg mb-8 bg-white/4">
                <form onSubmit={handelsearch} className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <label className="text-sm text-gray-300">Where</label>
                    <input type="text" placeholder="City" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={city} onChange={(e) => setCity(e.target.value)}/>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Check-in Date</label>
                    <input type="date" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={date_from} onChange={(e) => setDate_from(e.target.value)}/>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Check-out Date</label>
                    <input type="date" className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={date_to} onChange={(e) => setDate_to(e.target.value)}/>
                  </div>
                  <div>
                    <label className="text-sm text-gray-300">Guests</label>
                    <div className="flex gap-2">
                      <select className="py-2 px-2 border border-white/10 rounded-md w-full bg-transparent" value={guests} onChange={(e) => setGuests(Number(e.target.value))}>
                        <option className="text-black" value={1}>1 adult</option>
                        <option className="text-black" value={2}>2 adults</option>
                        <option className="text-black" value={4}>Family — 2 adults, 2 children</option>
                      </select>
                      <button type="submit" className="py-2 px-4 bg-blue-500/20 hover:bg-blue-500/40 rounded-md whitespace-nowrap transition">Search</button>
                      <button type="button" className="px-4 py-2 rounded-md border border-white/10 whitespace-nowrap" onClick={handleClearShearch}>Reset</button>
                    </div>
                  </div>
                </form>
            </div>
            <div className="flex gap-8">
              <form className="flex-1" onSubmit={handelfilter}>
                <div className="bg-white/4 p-4 rounded-lg flex flex-col gap-4">
                  <h4>Filters</h4>
                  <div>
                    <label className="text-sm text-white/80">Price ($)</label>
                    <div className="flex gap-4 mt-2">
                      <div className="flex flex-col">
                        <label className="text-xs text-white/80">From</label>
                          <input type="number" className="w-30 mt-2 border border-white/10 rounded-sm no-spin appearance-none"/>
                      </div>
                      <div className="flex flex-col"> 
                        <label className="text-xs text-white/80">To</label>
                          <input type="number" className="w-30 mt-2 border border-white/10 rounded-sm no-spin appearance-none"/>
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-white/80">Star Rating</label>
                    <div className="flex mt-4 gap-2">
                      <button className={`px-2 py-1 rounded-md border border-white text-sm ${stars == 5 && "bg-white/15"} `} type="button" onClick={() => setStars(5)}>5★</button>
                      <button className={`px-2 py-1 rounded-md border border-white text-sm ${stars == 4 && "bg-white/15"} `} type="button" onClick={() => setStars(4)}>4★+</button>
                      <button className={`px-2 py-1 rounded-md border border-white text-sm ${stars == 3 && "bg-white/15"} `} type="button" onClick={() => setStars(3)}>3★+</button>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-white/80">Facilities</label>
                    <div className="grid grid-cols-2 mt-4 gap-2 text-sm text-white/80">
                      {facilities.map(facilitie => (
                      <label className="flex items-center gap-2" key={facilitie.id}>
                        <input type="checkbox" onChange={() => addFacilities(facilitie.id)} />{facilitie.name}
                      </label>
                      ))}
                    </div>
                  </div>
                  <div>
                    <button className="w-full bg-blue-500/20 hover:bg-blue-500/40 py-2 rounded-lg transition mb-3 mt-2" type="submit">Apply</button>
                    <button className="w-full border border-white/10 py-2 rounded-lg transition" type="button" onClick={() => { setStars(0), setHotels([]), setActiveFilter(false)}}>Reset Filters</button>
                  </div>
                </div>
              </form>
              <div className="flex-3 flex-col">
                {hotelsToRender.length == 0 ? (
                  <div className="flex items-center justify-center">
                    <h1>No hotels found for your search</h1>
                  </div>
                  ) : hotelsToRender.map(hotel => 
                    <div className="bg-white/4 p-4 flex rounded-lg mb-4" key={hotel.id}>
                      <div className="flex flex-3">
                        <div className="mr-4 shrink-0">
                          <img className="w-50 h-50 rounded-lg" src={hotel.images?.length ? "http://127.0.0.1:8002" + hotel.images.find(img => img.is_main)?.image_url || "http://127.0.0.1:8002" + hotel.images[0].image_url : "https://cf.bstatic.com/xdata/images/hotel/square600/584421551.webp?k=14f2c7c8e5bc8a3e31f34d4b8c248f88a625cea9999abe481fce0c0d5ced559b&o=" }  alt=""/>
                        </div>
                        <div>
                          <a onClick={() => navigate(`/hotels/${hotel.id}`)} translate="no" className="font-bold cursor-pointer hover:underline">{hotel.name}</a>
                          <div className="flex mt-2 mb-3 items-center">
                            <svg className="h-6 w-6" viewBox="0 0 32 32" fill="currentColor"><path d="M16,1C9.925,1,5,5.925,5,12c0,10,10,19,11,19s11-9,11-19C27,5.925,22.075,1,16,1z M16,16 c-2.209,0-4-1.791-4-4c0-2.209,1.791-4,4-4s4,1.791,4,4C20,14.209,18.209,16,16,16z"></path></svg> <p className="text-sm">Hotel in <span translate="no"> {hotel.city}</span></p>
                          </div>
                          <p className="line-clamp-3 text-sm mr-2">{hotel.description}</p>
                        </div>
                      </div>
                      <div>
                        <div className="flex flex-1 flex-col text-right h-50">
                          <div className="flex justify-end items-center">
                            <h4 className="font-semibold mr-2">Stars: </h4><h5 className="bg-blue-500/20 py-1 px-3 rounded-md">{hotel.rating}</h5>
                          </div>
                          <div className="mt-auto mb-6">
                            <p className="text-xs text-white/80 mb-1">Price from:</p>
                            <h4 className="font-bold text-xl text-green-600">${hotel.price_per_night}</h4>
                          </div>
                          <button className="py-2 px-4 bg-blue-500/20 hover:bg-blue-500/40 rounded-md transition" onClick={() => navigate(`/hotels/${hotel.id}`)}>View details</button>
                        </div>
                      </div>
                    </div>
                  )
                }
              </div>
            </div>
        </div>    
      </>
    )
}

export default Hotels