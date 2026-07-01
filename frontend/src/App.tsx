import { Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import type { AppDispatch, RootState } from "./ts/store";
import { fetchFavoriteHotel, fetchMe } from "./ts/authSlice";
import MainLayout from "./layouts/MainLayout";
import EmptyLayout from "./layouts/EmptyLayout";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Hotels from "./pages/Hotels";
import Hotel from "./pages/Hotel";
import Profile from "./pages/Profile";
import CreateBooking from "./pages/CreateBooking";
import PayBooking from "./pages/PayBooking";
import VerifyEmail from "./pages/VerifyEmail";

function App() {
  const dispatch = useDispatch<AppDispatch>();
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  useEffect(() => {
    dispatch(fetchMe())
  }, [])

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchFavoriteHotel())
    }
  }, [isAuthenticated])

  return (
    <Routes>

      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/hotels" element={<Hotels />} />
        <Route path="/hotels/:hotelId" element={<Hotel />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/booking" element={<CreateBooking />} />
        <Route path="/booking/pay" element={<PayBooking />} />
      </Route>

      <Route element={<EmptyLayout />}>
        <Route path="/verify_email" element={<VerifyEmail />} />
      </Route>

    </Routes>
  )
}

export default App