import socket

def udp_client():
    # Создаем UDP-сокет
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Адрес сервера
    server_address = ('localhost', 65433)
    
    try:
        while True:
            message = input("Введите сообщение (или 'exit' для завершения): ")
            client_socket.sendto(message.encode(), server_address)

            if message.lower() == 'exit':
                print("Отправлена команда завершения. Закрытие клиента.")
                break

            data, server = client_socket.recvfrom(1024)
            print(f"Ответ от сервера: {data.decode()}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    udp_client()
