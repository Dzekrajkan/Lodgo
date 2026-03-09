import { useDispatch, useSelector } from "react-redux";
import { Link, useNavigate } from "react-router-dom"
import type { AppDispatch, RootState } from "../ts/store"
import React, { useEffect, useState } from "react";
import { fetchRegister } from "../ts/authSlice";
import { useNotify } from "../components/Notify";

function Register () {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { notify } = useNotify();
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/profile")
    }
  }, [isAuthenticated])

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (username.trim().length < 3) return notify("The name must be at least 3 characters long.", "msg")

    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(String(email).trim())) return notify("Incorrect email", "msg")

    if (password1.trim().length == 0) return notify("Fill in the password field", "msg")

    if (password1.trim().length < 8) return notify("The password must be at least 8 characters long.", "msg")

    if (password1 !== password2) return notify("The passwords don't match", "msg")

    try {
        await dispatch(fetchRegister({ username, email, password1, password2 })).unwrap();
        return notify("Registration successful, confirmation email sent to email", "success")
    } catch (err: any) {
        notify(err || "Registration failed", "error")
      }
    }

  return (
    <>
      <div className="flex items-center justify-center mt-20 mb-20">
        <div className="max-w-4xl w-full mx-4 grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div className="shadow-lg flex flex-col gap-6 p-8 rounded-2xl bg-white/4">
                <a href="" className="font-bold text-xl mb-4" translate="no">Lodgo</a>
                <div className="mb-4">
                    <h2 className="font-bold text-2xl mb-2">Welcome to <span translate="no"> Lodgo</span></h2>
                    <p className="text-gray-300">Manage bookings, get the best prices, and keep tickets in one place.</p>
                </div>
                <div>
                    <img src="https://img.freepik.com/free-photo/luxury-villa-with-infinity-pool-sunset-coastal-view_23-2151986080.jpg?semt=ais_hybrid&w=740&q=80" className="h-48 w-full rounded-lg" alt="" />
                </div>
                <div>
                    <p className="text-sm text-white/70 mt-auto">Need help? <a href="" className="underline">Contact Support</a></p>
                </div>
            </div>
            <div className="shadow-lg p-6 rounded-2xl bg-white/4">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="font-semibold text-xl">Create Account</h2>
                    <p className="text-sm">Already have an account? <Link to="/login" className="text-indigo-300 underline">Sign In</Link></p>
                </div>
                <div className="mb-4">
                    {
                      //<button className="w-full py-2 border border-white/10 bg-white/10 rounded-lg">Войти через Google</button>
                    }
                </div>
                <div className="relative py-2 text-sm text-white/60 my-6">
                    <div className="absolute left-0 right-0 top-1/2 border-t border-white"></div>
                </div>
                <form action="" className="space-y-4" onSubmit={handleRegister}>
                    <div>
                        <label htmlFor="">Full Name</label>
                        <input type="text" placeholder="Ivan Ivanov" className="py-2 w-full px-2 border border-white/10 rounded-lg" value={username} onChange={(e) => setUsername(e.target.value)}/>
                    </div>
                    <div className="flex flex-col">
                        <label htmlFor="" className="text-sm mb-1">Email</label>
                        <input type="text" placeholder="you@example.com" className="py-2 w-full px-2 border border-white/10 rounded-lg" value={email} onChange={(e) => setEmail(e.target.value)}/>
                    </div>
                    <div className="flex flex-col">
                        <label htmlFor="" className="text-sm mb-1">Password</label>
                        <input type="password" placeholder="Enter your password" className="py-2 w-full px-2 border border-white/10 rounded-lg" value={password1} onChange={(e) => setPassword1(e.target.value)}/>
                    </div>
                    <div>
                        <label htmlFor="">Confirm Password</label>
                        <input type="password" placeholder="Repeat password" className="py-2 w-full px-2 border border-white/10 rounded-lg" value={password2} onChange={(e) => setPassword2(e.target.value)}/>
                    </div>
                    <div>
                        <button className="bg- w-full py-2 rounded-md bg-blue-500/20 hover:bg-blue-500/40" type="submit">Create Account</button>
                    </div>
                </form>
            </div>
        </div>
      </div>
    </> 
  )
}

export default Register