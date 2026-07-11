def test_add_favorite_success(authorized_client, test_hotel):
    res = authorized_client.post("/api/favorite", params={"status": "add"}, json={"hotel_id": test_hotel.id},)

    assert res.status_code == 200
    data = res.json()
    assert data["hotel"]["id"] == test_hotel.id

def test_add_favorite_already_exists(authorized_client, test_hotel):
    first = authorized_client.post("/api/favorite", params={"status": "add"}, json={"hotel_id": test_hotel.id},)
    second = authorized_client.post("/api/favorite", params={"status": "add"}, json={"hotel_id": test_hotel.id},)

    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]

def test_remove_favorite_success(authorized_client, test_hotel):
    authorized_client.post("/api/favorite", params={"status": "add"}, json={"hotel_id": test_hotel.id},)
    res = authorized_client.post("/api/favorite", params={"status": "remove"}, json={"hotel_id": test_hotel.id},)

    assert res.status_code == 200
    assert res.json()["success"] == "removed"

def test_remove_favorite_not_found(authorized_client, test_hotel):
    res = authorized_client.post("/api/favorite", params={"status": "remove"}, json={"hotel_id": test_hotel.id},)

    assert res.status_code == 400
    assert res.json()["detail"] == "You don't have this hotel in your favorites."

def test_get_favorites(authorized_client, test_hotel):
    authorized_client.post("/api/favorite", params={"status": "add"}, json={"hotel_id": test_hotel.id},)
    res = authorized_client.get("/api/favorite")

    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["hotel"]["id"] == test_hotel.id

def test_favorite_invalid_status(authorized_client, test_hotel):
    res = authorized_client.post("/api/favorite", params={"status": "not-a-real-status"}, json={"hotel_id": test_hotel.id},)

    assert res.status_code == 400
    assert res.json()["detail"] == "Invalid status. Use 'add' or 'remove'."