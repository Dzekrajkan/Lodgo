import { useDispatch, useSelector } from "react-redux"
import { Link, useNavigate } from "react-router-dom"
import type { AppDispatch, RootState } from "../ts/store"
import { useEffect, useState } from "react";
import { fetchLogin } from "../ts/authSlice";
import { useNotify } from "../components/Notify";

function Login () {
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>();
  const { notify } = useNotify();
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (isAuthenticated) {
        navigate("/profile")
    }
  }, [isAuthenticated])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(String(email).trim())) return notify("Incorrect email", "msg")

    if (password.trim().length == 0) return notify("Fill in the password field", "msg")

    if (password.trim().length < 8) return notify("The password must be at least 8 characters long.", "msg")

    try {
      await dispatch(fetchLogin({ email, password })).unwrap();
      navigate("/");
    } catch (err: any) {
        notify(err || "Login failed", "error")
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
                    <p className="text-gray-300">Manage your bookings, get the best prices, and keep your tickets all in one place.</p>
                </div>
                <div>
                    <img src="https://img.freepik.com/free-photo/luxury-villa-with-infinity-pool-sunset-coastal-view_23-2151986080.jpg?semt=ais_hybrid&w=740&q=80" className="h-48 w-full rounded-lg" alt="" />
                </div>
                  <div>
                      <p className="text-sm text-white/70 mt-auto">Need help? <a href="" className="underline">Contact Support</a></p>
                  </div>
            </div>
            <div className="shadow-lg px-6 py-8 rounded-2xl bg-white/4">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="font-semibold text-xl">Sign in to your account</h2>
                    <p className="text-sm">Don't have an account? <Link to="/register" className="text-indigo-300 underline">Register</Link></p>
                </div>
                <div className="mb-4">
                    {
                    //<button className="w-full py-2 border border-white/10 bg-white/10 rounded-lg">Sign in with Google</button>
                    }
                </div>
                <div className="relative py-2 text-sm text-white/60 my-6">
                    <div className="absolute left-0 right-0 top-1/2 border-t border-white"></div>
                </div>
                <form action="" className="space-y-5" onSubmit={handleLogin}>
                    <div className="flex flex-col">
                        <label htmlFor="" className="text-sm mb-1">Email</label>
                        <input type="text" placeholder="you@example.com" className="py-2 w-full px-2 border border-white/10 rounded-lg" value={email} onChange={(e) => setEmail(e.target.value)}/>
                    </div>
                    <div className="flex flex-col">
                        <label htmlFor="" className="text-sm mb-1">Password</label>
                        <input type="password" placeholder="Enter password" className="py-2 w-full px-2 border border-white/10 rounded-lg" value={password} onChange={(e) => setPassword(e.target.value)}/>
                    </div>
                    <div>
                        <button className="w-full py-2 rounded-md bg-blue-500/20 hover:bg-blue-500/40">Sign in</button>
                    </div>
                </form>
            </div>
        </div>
      </div>
    </>
  )
}

export default Login