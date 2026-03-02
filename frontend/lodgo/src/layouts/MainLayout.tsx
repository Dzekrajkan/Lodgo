import { Outlet, NavLink, useNavigate } from "react-router-dom"
import { useDispatch, useSelector } from "react-redux"
import type { AppDispatch, RootState } from "../ts/store"
import { fetchLogout } from "../ts/authSlice"

function MainLayout() {
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated)

  return (
    <div className="min-h-screen bg-[#070B14] text-white relative overflow-hidden">
      <div className="flex justify-between max-w-7xl mx-auto p-6 bg-white/2 rounded-2xl mt-6 border border-white/10 backdrop-blur-xl mb-5">
        <a href="">
          <div>

          </div>
          <span className="font-bold text-2xl" onClick={() => navigate("/")} translate="no">Lodgo</span>
        </a>

        <nav role="navigation" className="gap-6 flex items-center text-sm">
          <NavLink to="/" className="text-white/70 hover:text-white transition">Home</NavLink>
          <NavLink to="/hotels" className="text-white/70 hover:text-white transition">Hotels</NavLink>
        </nav>

        <div className="gap-3 flex">
          {isAuthenticated == true ? 
          <>
            <div className="bg-white rounded-full w-10 h-10" onClick={() => navigate("/profile")}></div>
            <button className="px-3 py-1 rounded-md border border-white/10 bg-white/5 hover:bg-white/10 transition" onClick={() => {dispatch(fetchLogout())}}>Logout</button>
          </>
           : 
           <>
            <button onClick={() => navigate("login")} className="py-2 px-4 text-sm">Login</button>
            <button onClick={() => navigate("register")} className="bg-gradient-to-r bg-blue-500/20 hover:bg-blue-500/40 p-2 px-4 rounded-md font-semibold text-white hover:scale-105 transition">Register</button>
           </> 
          }
        </div>
      </div>

      <Outlet />

      <footer className="border-t mt-20 max-w-7xl mx-auto">
        <div className="grid grid-cols-3 mt-10">
          <div>
            <h3 translate="no">Lodgo</h3>
            <p className="text-xs">Best hotels at the best prices</p>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Navigation</h3>
            <ul className="space-y-2 text-white/60 text-sm">
              <li><NavLink to="/" className="hover:text-white transition">Home</NavLink></li>
              <li><NavLink to="hotels" className="hover:text-white transition">Hotels</NavLink></li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold mb-4">Contacts</h3>
            <p className="flex flex-col text-sm text-white/60">
              support@lodgo.example<br />
              +380 44 123 4567
            </p>
            <div className="flex mt-4 gap-3">
              <div className="w-9 h-9 flex items-center justify-center">F</div>
              <div className="w-9 h-9 flex items-center justify-center">T</div>
              <div className="w-9 h-9 flex items-center justify-center">I</div>
            </div>
          </div>
        </div>
        <div className="text-center mt-10 mb-20 text-sm text-white/40">© 2026 <span translate="no"> Lodgo</span>. All rights reserved.</div>
      </footer>

    </div>
  )
}

export default MainLayout