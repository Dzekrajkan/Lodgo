def test_get_hotels_empty(client):
    res = client.get("/api/hotels")
    
    assert res.status_code == 200
    res = res.json()
    assert res == []

def test_get_hotels(client, test_hotel):
    res = client.get("/api/hotels")

    assert res.status_code == 200
    res = res.json()
    assert res != []

def test_get_hotel_by_id(client, test_hotel):
    res = client.get(f"/api/hotels/{test_hotel.id}")

    assert res.status_code == 200

def test_get_hotel_not_found(client):
    res = client.get("/api/hotels/99999")
    
    assert res.status_code == 400

def test_search_hotels(client, test_room):
    res = client.get("/api/hotels/search", params={"city": "FEFEF", "date_from": "2026-01-01", "date_to": "2026-01-30", "guests": 1})

    assert res.status_code == 200

def test_search_hotels_invalid_dates(client, test_room):
    res = client.get("/api/hotels/search", params={"city": "FEFEF", "date_from": "2026-01-30", "date_to": "2026-01-01", "guests": 1})

    assert res.status_code == 400

def test_get_rooms(client, test_room, test_hotel):
    res = client.get(f"/api/hotels/{test_hotel.id}/rooms", params={"date_from": "2026-01-01", "date_to": "2026-01-30", "guests": 1})

    assert res.status_code == 200

def test_get_rooms_hotel_not_found(client, test_room):
    res = client.get("/api/hotels/99999/rooms", params={"date_from": "2026-01-01", "date_to": "2026-01-30", "guests": 1})

    assert res.status_code == 400