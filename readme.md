This project is a scalable backend system designed to handle real-time job processing across distributed print shops via WebSocket communication. It uses Python's `aiohttp` for the web server and `websockets` for real-time communication. The system is built to be robust, handling tasks concurrently and ensuring fair processing without starvation.

## Features

- **WebSocket-based Real-time Communication**: Enables real-time updates and communication between clients and the server.
- **Queue System**: Manages job processing efficiently, preventing starvation and ensuring fair handling of tasks.
- **Asynchronous Python**: Built using `aiohttp` and `websockets`, providing non-blocking, scalable performance.
- **Supabase Integration**: Interacts with Supabase for database operations, managing jobs and their statuses.
- **Error Handling and Resilience**: Includes retry mechanisms, exponential backoff, and graceful shutdown to ensure system stability.

## Technologies Used

- **Python**: Core programming language.
- **Aiohttp**: Web framework for asynchronous HTTP services.
- **WebSockets**: Real-time communication protocol.
- **Supabase**: Backend-as-a-service used for database operations.
- **Docker** (Optional): For containerized deployment.