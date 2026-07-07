export interface Facility {
    id: number
    name: string
}

export interface Service {
    id: number
    hotel_id: number
    name: string
    price: number
}

export interface HotelImage {
    id: number
    image_url: string
    is_main: boolean
}

export interface Hotel {
    id: number
    owner_id: number
    name: string
    description: string
    address: string
    city: string
    country: string
    latitude: string
    longitude: string
    price_per_night: number
    check_in_time: string
    check_out_time: string
    rating: number
    reviews_count: number
    facilities: Facility[]
    images: HotelImage[]
    services: Service[]
}

export interface RoomImage {
    id: number
    image_url: string
    is_main: boolean
}


export interface Room {
    id: number
    hotel_id: number
    name: string
    description: string
    price_per_night: number
    quantity: number
    capacity: number
    available: number
    images: RoomImage[]
}

export interface Booking {
    id: number
    user_id: number
    room_id: number
    hotel_id: number
    total_price: number
    status: "pending" | "confirmed" | "cancelled" | "completed"
    date_from: string
    date_to: string
    created_at: string
    hotel: Hotel
    room: Room
}

export interface User {
    id: number
    username: string
    email: string
    is_verified: boolean
    created_at: string
}

export interface FavoriteHotel {
    id: number
    created_at: string
    hotel: Hotel
}

export interface Review {
    id: number
    user_id: number
    hotel_id: number
    booking_id: number
    rating: number
    comment: string
    created_at: string
    user: {
        id: number
        username: string
    }
}