export function formatBookingDates(dateFrom: string, dateTo: string) {
  const from = new Date(dateFrom)
  const to = new Date(dateTo)

  const dayFrom = from.getDate()
  const dayTo = to.getDate()

  const monthFrom = from.toLocaleString("en-En", { month: "long" })
  const monthTo = to.toLocaleString("en-En", { month: "long" })

  if (monthFrom === monthTo) {
    return `${dayFrom}–${dayTo} ${monthFrom}`
  }

  return `${dayFrom} ${monthFrom} – ${dayTo} ${monthTo}`
}
