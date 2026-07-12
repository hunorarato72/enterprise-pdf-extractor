import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """
    Ez egy pytest fixture, ami egy FastAPI TestClient-et biztosít.
    A tesztjeink ezt a klienst fogják paraméterként megkapni,
    így szimulálhatunk HTTP kéréseket az API végpontjainkra.
    Olyan, mint a Spring Boot TestRestTemplate vagy a C# WebApplicationFactory.
    """
    # A TestClient segítségével memóriában tudjuk tesztelni a végpontokat
    # anélkül, hogy ténylegesen elindítanánk a webszervert egy porton.
    with TestClient(app) as c:
        yield c
