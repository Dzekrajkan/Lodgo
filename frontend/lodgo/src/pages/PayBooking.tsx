import React, { useState } from "react"
import { useLocation } from "react-router-dom"
import api from "../ts/axiosInstance"
import { useNotify } from "../components/Notify"
import axios from "axios"

function PayBooking() {
    const { notify } = useNotify()
    const location = useLocation()
    const { id, total_price, name_hotel, name_room, date_from, date_to, guests } = location.state as {
        id: number,
        total_price: number,
        name_hotel: string,
        name_room: string,
        date_from: string,
        date_to: string,
        guests: number
    }
    const [username, setUsername] = useState("");
    const [cardNumber, setCardNumber] = useState("")
    const [cardExpirationDate, setCardExpirationDate] = useState("")
    const [CVC, setCVC] = useState("")

    const formatDate = (date: string) => {
        return new Date(date).toLocaleDateString("en-GB", {
            day: "numeric",
            month: "short"
        })
    }

    const handelPayBooking = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (username.length <= 3) return notify("Enter your username", "msg")
        if (cardNumber.replace(/\s/g, "").length !== 16) return notify("The card number must contain 16 characters.", "msg")
        if (cardExpirationDate.length !== 5) return notify("Enter expiration date", "msg")
        if (CVC.length !== 3) return notify("The CVC code must consist of 3 characters.", 'msg')

        try {
            const res = await api.post("/bookings/pay", { id: id, username: username, card_number: cardNumber, card_expiration_date: cardExpirationDate, CVC: CVC }, {
                headers: { "Content-Type": "application/json" },
                withCredentials: true,
            });
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
          <div className="max-w-6xl mx-auto px-6 pb-20">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white/6 p-6 rounded-xl">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h1 className="text-2xl font-bold mb-1">Booking Payment</h1>
                                <p className="text-sm text-white/70">Review the details and confirm the payment. You'll receive an electronic receipt by email.</p>
                            </div>
                            <div className="text-sm text-white/60">
                                Step <strong> 2 </strong> of 2
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="bg-gradient-to-tr from-indigo-700 to-sky-700 p-5 rounded-2xl">
                                <div className="flex justify-between items-center mb-8">
                                    <div className="py-4 px-6 bg-gradient-to-br from-yellow-200 to-orange-500 rounded-md"></div>
                                    <div className="ml-auto text-sm text-white/70">VISA •••• 4242</div>
                                </div>
                                <div className="mb-6">
                                    <h3 className="text-lg tracking-widest font-mono">**** **** **** 4242</h3>
                                </div>
                                <div className="flex justify-between mb-6">
                                    <div>
                                        <div className="text-xs text-white/60">NAME</div>
                                        <div className="font-medium text-sm text-white/80">IVAN IVANOV</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-white/60">EXPIRY</div>
                                        <div className="font-medium text-sm text-white/80">12/26</div>
                                    </div>
                                </div>
                            </div>
                            <div className="p-4">
                                <div className="mb-4">
                                    <h3 className="font-semibold mb-3">Security & Support</h3>
                                    <ul className="space-y-2 text-sm text-white/70">
                                        <li>🔒 Data encryption</li>
                                        <li>📩 Automatic electronic receipt</li>
                                        <li>🤝 Refund within 14 days</li>
                                    </ul>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="px-3 py-2 rounded-lg text-sm">PCI DSS</div>
                                    <div className="px-3 py-2 rounded-lg text-sm">3-D Secure</div>
                                    <div className="ml-auto text-sm text-white/60">Support: <a href="" className="underline" translate="no">support@lodgo.example</a></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <form className="bg-white/6 p-6 rounded-xl" onSubmit={handelPayBooking}>
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div className="col-span-2">
                            <label htmlFor="" className="text-sm text-white/70">Name on card</label>
                            <input type="text" placeholder="IVAN IVANOV" className="mt-2 w-full rounded-lg px-3 py-2 border border-gray-600/15" value={username} onChange={(e) => setUsername(e.target.value)} required/>   
                        </div>
                        <div className="col-span-2">
                            <label htmlFor="" className="text-sm text-white/70">Card number</label>
                            <input type="text" inputMode="numeric" maxLength={20} placeholder="1234 5678 0912 3456" className="mt-2 w-full rounded-lg px-3 py-2 border border-gray-600/15" value={cardNumber} onChange={(e) => { 
                                const value = e.target.value.replace(/\D/g, "").slice(0,16)
                                const formatted = value.replace(/(.{4})/g, "$1 ").trim()
                                setCardNumber(formatted)
                            }} required/>   
                        </div>
                        <div>
                            <label htmlFor="" className="text-sm text-white/70">Expiry (MM/YY)</label>
                            <input type="text" inputMode="numeric" maxLength={5} placeholder="MM/YY" className="mt-2 w-full rounded-lg px-3 py-2 border border-gray-600/15" value={cardExpirationDate}   onChange={(e) => {
                                let value = e.target.value.replace(/\D/g, "").slice(0, 4)
                                if (value.length >= 3) value = value.slice(0, 2) + "/" + value.slice(2)
                                console.log(value)
                                setCardExpirationDate(value)
                            }} required/>
                        </div>
                        <div>
                            <label htmlFor="" className="text-sm text-white/70">CVC</label>
                            <input type="text" inputMode="numeric" maxLength={3} placeholder="123" className="mt-2 w-full rounded-lg px-3 py-2 border border-gray-600/15" value={CVC}   onChange={(e) => {
                                const value = e.target.value.replace(/\D/g, "").slice(0, 3)
                                setCVC(value)
                            }} required/>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 lg:grid-cols-2 items-center">
                        <div className="text-sm text-white/70">
                            <div>Amount to pay</div>
                            <div className="text-2xl font-bold text-indigo-300">$ {total_price}</div>
                            <div className="text-xs text-white/60">This amount will be charged after confirmation.</div>
                        </div>
                        <div className="md:justify-self-end">
                            <button className="py-3 px-8 bg-blue-500/20 hover:bg-blue-500/40 transition rounded-xl font-semibold shadow-lg hover:scale-105" type="submit">Pay</button>
                        </div>
                      </div>
                    </form>
                </div>
                <aside className="space-y-6">
                    <div className="p-6 rounded-xl shadow-lg bg-white/4">
                        <h3 className="text-lg font-semibold mb-4">Booking Summary</h3>
                        <div className="text-white/70 text-sm mb-4 space-y-3">
                            <div className="flex justify-between">
                                <span>Hotel</span>
                                <span className="text-right">{name_hotel}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Room</span>
                                <span className="text-right">{name_room}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Dates</span>
                                <span className="text-right">{formatDate(date_from)} - {formatDate(date_to)}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Guests</span>
                                <span className="text-right">{guests}</span>
                            </div>
                            <div className="flex justify-between border-t pt-3">
                                <span>Total</span>
                                <span className="text-right">$ {total_price}</span>
                            </div>
                        </div>
                        <div className="text-xs text-white/60">Need help? Contact support</div>
                    </div>
                    <div className="p-4 rounded-2xl shadow-lg bg-white/4 text-sm text-white/70">
                        <h3 className="font-semibold mb-2">Supported cards</h3>
                        <div className="flex items-center gap-3">
                            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='30'%3E%3Crect width='48' height='30' rx='4' fill='%23F79E1B'/%3E%3C/svg%3E" className="w-12 h-8 rounded-sm shadow" />
                            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='30'%3E%3Crect width='48' height='30' rx='4' fill='%23EA4335'/%3E%3C/svg%3E" className="w-12 h-8 rounded-sm shadow" />
                            <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='30'%3E%3Crect width='48' height='30' rx='4' fill='%23000'/%3E%3C/svg%3E" className="w-12 h-8 rounded-sm shadow" />
                        </div>
                    </div>
                </aside>
            </div>
          </div>
        </>
    )
}

export default PayBooking