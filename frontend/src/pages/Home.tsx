import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useNotify } from "../components/Notify"

function Home() {
    const navigate = useNavigate()
    const { notify } = useNotify()
    const [city, setCity] = useState("")
    const [date_from, setDate_from] = useState("")
    const [date_to, setDate_to] = useState("")
    const [guests, setGuests] = useState(1)

    const handelsearch = async () => {
      if (city.length <= 0) return notify("Enter city", "msg");
      if (date_from.length <= 0) return notify("Enter your arrival date", "msg");
      if (date_to.length <= 0) return notify("Enter your departure date", "msg");

      navigate("/hotels", {
        state: {
          city_u: city,
          date_from_u: date_from,
          date_to_u: date_to,
          guests_u: guests
        }
      }) 
    }

  return (
    <>
      <div className="max-w-7xl mx-auto px-6">
        <section className="reletive grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-7">
                <h1 className="text-4xl md:text-5xl font-extrabold mb-4">Find the perfect hotel for your trip</h1>
                <p className="text-lg text-white/70">Compare prices, see real photos and reviews, book instantly — all in one place.</p>
                <div className="mt-6 bg-white/3 rounded-2xl p-6 shadow-lg max-w-2xl mb-8">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <label htmlFor="" className="text-sm text-white/70">Where</label>
                      <input type="text" placeholder="City" className="py-2 px-2 border border-white/10 rounded-md w-full" value={city} onChange={(e) => setCity(e.target.value)}/>
                    </div>
                    <div>
                        <label htmlFor="" className="text-sm text-white/70">Guests</label>
                        <select className="py-2 px-2 border border-white/10 rounded-md w-full" value={guests} onChange={(e) => setGuests(Number(e.target.value))}>
                          <option className="text-black" value={1}>1 adult</option>
                          <option className="text-black" value={2}>2 adults</option>
                          <option className="text-black" value={4}>Family — 2 adults, 2 children</option>
                        </select>
                    </div>
                    <div>
                      <label htmlFor="" className="text-sm text-white/70">Check-in Date</label>
                      <input type="date" placeholder="Feb 14 - 17" className="py-2 px-2 border border-white/10 rounded-md w-full" value={date_from} onChange={(e) => setDate_from(e.target.value)}/>
                    </div>
                    <div>
                      <label htmlFor="" className="text-sm text-white/70">Check-out Date</label>
                      <input type="date" placeholder="Feb 14 - 17" className="py-2 px-2 border border-white/10 rounded-md w-full" value={date_to} onChange={(e) => setDate_to(e.target.value)}/>
                    </div>
                  </div>
                  <div className="grid grid-cols-4 text-white/70 text-xs gap-3">
                    <div className="flex items-center">Fast Booking</div>
                    <div className="flex items-center">Best Price Guarantee</div>
                    <div className="flex items-center">24/7 Support</div>
                    <div className="flex items-center">Transparent Terms</div>
                  </div>
                </div>
                <div className="">
                  <button className="py-3 px-16 mr-4 bg-blue-500/20 hover:bg-blue-500/40 rounded-md hover:scale-105 transition" onClick={handelsearch}>Search</button>
                  <button className="text-sm text-white/80 underline" onClick={() => navigate("/hotels")}>View All Hotels</button>
                </div>
            </div>
            <div className="lg:col-span-5 relative">
                <div className="rounded-3xl overflow-hidden">
                    <img src="https://img.freepik.com/free-photo/luxury-villa-with-infinity-pool-sunset-coastal-view_23-2151986080.jpg?semt=ais_hybrid&w=740&q=80" alt="" className=""/>
                </div>
                <div>

                </div>
            </div>
        </section>
          <section className="mt-10">
            <div className="flex flex-col items-center justify-center">
              <h3 className="font-bold text-2xl mb-2">What Our Guests Say</h3>
              <p className="text-white/70 mb-5">Real reviews and ratings — we care about your comfort.</p>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-white/5 p-6 rounded-xl">
                  <p className="text-sm text-gray-200 mb-4">"The hotel exceeded expectations: clean, polite staff, and great breakfast. Recommended for business trips."</p>
                  <div className="flex gap-3">
                    <img src="https://api.dicebear.com/9.x/avataaars/svg?seed=Olga" alt="Ольга" className="w-12 h-12 rounded-full object-cover" />
                    <div>
                      <h4 className="font-semibold">Olga, Kyiv</h4>
                      <p className="text-xs text-gray-400">Business Trip</p>
                    </div>
                  </div>
                </div>
                <div className="bg-white/5 p-6 rounded-xl">
                  <p className="text-sm text-gray-200 mb-4">"Loved the location and room cleanliness. Convenient for family trips — playground nearby."</p>
                  <div className="flex gap-3">
                    <img src="https://api.dicebear.com/9.x/avataaars/svg?seed=п" alt="Ігор" className="w-12 h-12 rounded-full object-cover" />
                    <div>
                      <h4 className="font-semibold">Igor, Lviv</h4>
                      <p className="text-xs text-gray-400">With Family</p>
                    </div>
                  </div>
                </div>
                <div className="bg-white/5 p-6 rounded-xl">
                  <p className="text-sm text-gray-200 mb-4">"Friendly staff and quick check-in. Modern room with everything needed — will return."</p>
                  <div className="flex gap-3">
                    <img src="https://api.dicebear.com/9.x/avataaars/svg?seed=Lina" alt="Ліна" className="w-12 h-12 rounded-full object-cover" />
                    <div>
                      <h4 className="font-semibold">Lina, Odesa</h4>
                      <p className="text-xs text-gray-400">Weekend</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
      </div>
    </>
  )
}

export default Home