interface Facilities {
    id: number,
    name: string
}

interface HotelImg {
    id: number,
    hotel_id: number,
    image_url: string,
    is_main: boolean
}

interface Services {
    id: number,
    name: string,
    price: number
}

interface Hotel {
    id: number,
    name: string,
    description: string,
    owner_id: number,
    address: string,
    city: string,
    country: string,
    latitude: string,
    longitude: string,
    price_per_night: number,
    check_in_time: string,
    check_out_time: string,
    rating: number,
    reviews_count: number,
    created_at: string,
    facilities: Facilities[],
    images: HotelImg[],
    services: Services[]
}

interface Room {
    id: number,
    hotel_id: number,
    name: string,
    description: string,
    price_per_night: number,
    quantity: number,
    capacity: number,
    available: number
}

interface Bookings {
    id: number,
    room_id: number,
    user_id: number,
    hotel_id: number,
    total_price: number,
    status: string,
    date_from: string,
    date_to: string,
    created_at: string,
    hotel: Hotel,
    room: Room
}

export type { Hotel, Room, Bookings, Facilities, Services }