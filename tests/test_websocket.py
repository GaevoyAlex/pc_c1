import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/market/tokens/bitcoin/price"
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Подключен к {uri}")
            
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("Отправлен ping")
            
            for i in range(10):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=35.0)
                    data = json.loads(message)
                    
                    if data["type"] == "price_update":
                        price_data = data["data"]
                        print(f"Обновление цены {price_data['symbol']}: ${price_data['price']:.2f} "
                              f"(изменение 24ч: {price_data['price_change_24h']:.2f}%)")
                    elif data["type"] == "pong":
                        print("Получен pong")
                    
                except asyncio.TimeoutError:
                    print("Таймаут ожидания сообщения")
                    break
                    
    except Exception as e:
        print(f"Ошибка WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())