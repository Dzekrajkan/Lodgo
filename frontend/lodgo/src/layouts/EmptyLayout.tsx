import { Outlet } from "react-router-dom"

function EmptyLayout() {
  return (
    <div className="min-h-screen bg-[#070B14] text-white flex items-center justify-center">
      <Outlet />
    </div>
  )
}

export default EmptyLayout