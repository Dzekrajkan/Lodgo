import { Star } from "lucide-react"

interface StarRatingProps {
    rating: number
    max?: number
}

export function StarRating({ rating, max = 5 }: StarRatingProps) {
    return (
        <div className="flex items-center gap-0.5">
            {Array.from({ length: max }, (_, i) => (
                <Star key={i} className={`h-4 w-4 ${i < Math.round(rating) ? "fill-white text-white-400" : "fill-none text-white/30"}`}/>
            ))}
        </div>
    )
}