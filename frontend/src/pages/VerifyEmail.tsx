import { useSelector } from "react-redux"
import type { RootState } from "../ts/store"
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import api from "../ts/axiosInstance";

function VerifyEmail() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams();
    const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);
    const token = searchParams.get("token")
    const [status, setStatus] = useState("loading");
    const [message, setMessage] = useState("");

    useEffect(() => {
        if (isAuthenticated) {
            navigate("/")
            return
        }

        if (!token) {
            setStatus("error")
            setMessage("Invalid confirmation link")
            return
        }

        else {
            const fetchToken = async () => {
                try {
                    const res = await api.get(`/auth/verify?&token=${token}`)
                    setMessage(res.data.success || "Email confirmed")
                    setStatus("success");
                } catch(err: any) {
                    setMessage(err.response?.data?.detail || "Confirmation error")
                    setStatus("error")
                }
            }
        fetchToken()
        }
    }, [isAuthenticated, token])

    return (
        <div className="min-h-screen flex items-center justify-center px-4">
            <div className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 text-center shadow-xl">
                {status === "loading" && (
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-12 h-12 border-4 border-white/20 border-t-blue-500 rounded-full animate-spin"></div>
                        <p className="text-white/70 text-sm">Verifying your email...</p>
                    </div>
                )}

                {status === "success" && (
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-14 h-14 rounded-full bg-green-500/20 flex items-center justify-center">
                            <span className="text-green-400 text-2xl">✓</span>
                        </div>
                        <h2 className="text-xl font-semibold">Email Verified</h2>
                        <p className="text-white/60 text-sm">{message}</p>
                        <button onClick={() => navigate("/login")} className="mt-4 w-full py-2 rounded-lg bg-blue-500/20 hover:bg-blue-500/40 transition font-semibold">Перейти ко входу</button>
                    </div>
                )}

                {status === "error" && (
                    <div className="flex flex-col items-center gap-4">
                        <div className="w-14 h-14 rounded-full bg-red-500/20 flex items-center justify-center">
                            <span className="text-red-400 text-2xl">✕</span>
                        </div>
                        <h2 className="text-xl font-semibold">Verification Error</h2>
                        <p className="text-white/60 text-sm">{message}</p>
                        <button onClick={() => navigate("/register")} className="mt-4 w-full py-2 rounded-lg bg-red-500/20 hover:bg-red-500/40 transition font-semibold">Зарегистрироваться снова</button>
                    </div>
                )}
            </div>
        </div>
    )
}

export default VerifyEmail