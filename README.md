# Async Task Processing System with AWS Deployment

This project demonstrates a production-ready asynchronous task processing system (i.e Deployed in EC2 using Pulumi explained in infra-branch) using: 

 **Flask** as (Web + API), **Celery** as (Task Queue Executor) , **RabbitMQ** as (Message Broker) , **Redis** as (Result Backend) , **Flower** as (Monitoring UI) , **Docker** as (Multi-service orchestration)


## Project Overview

This project is divided into 3 Labs, each Lab shows various implementation with techonology tools:

- **Lab-1-Async-Tasks**: System Design in Local machine and Poridhi lab implementation ([Read more](README.md))
- **Lab-2-Single-Instance**: Pulumi-Driven AWS Deployment steps (single EC2 instance) ([Read more](https://github.com/MD-Junayed000/async-tasks/blob/main/Lab-2-Single-Instance/README.md))
- **Lab-3-Multi-EC2**: Multi-EC2 instance deployment ([Read more](https://github.com/MD-Junayed000/async-tasks/blob/main/Lab-3-Multi-EC2/README.md))




>  **Objective**: Design a system that allows users to submit tasks asynchronously from a Flask API, execute them reliably in the background using Celery, queue tasks in RabbitMQ, and store task states and results in a backend db (redis).

---

##  System Architecture :
<img src="assets/Try-Page.svg" alt="Implementation Diagram" width="1000">

***1. User Request via API :***
 user interacts with the frontend UI to trigger a task—such as sending an email, reversing a text, or analyzing sentiment. This action sends an HTTP request to the Flask backend through a specific API endpoint.

***2.  Flask App: Receiving & Dispatching***
 Receives request and pushes task to Celery using delay().Flask responds to the user immediately with a confirmation message and a task_id, ensuring the experience remains fast and non-blocking.


***3. Celery as the Producer***
When .delay() is called, Celery acts as a task producer—serializing the task and sending it to the RabbitMQ message broker.

***4. RabbitMQ: Message Broker Layer***
RabbitMQ receives the serialized task and places it in a queue (commonly named celery_see).plays the role of a message router, managing queues and delivering tasks to any available consumer (Celery workers). It ensures decoupling between producers (Flask) and consumers (workers), allowing each part to scale independently.In these case:

<div align="center">
  <img src="assets/queue.svg" alt="Broker Diagram" width="700">
</div>

* Consumer = Celery Worker

* Exchange = Implicit direct exchange

* Queue = celery_see (task queue)


***5. Celery Workers: Task Execution Engine***

Celery workers continuously listen for tasks on the RabbitMQ queue. When a task becomes available, a worker pulls it, executes the defined function (like sending an email or reversing a string), and processes it in the background. With --concurrency enabled, workers can process multiple tasks in parallel, significantly improving throughput and responsiveness.



***6. Redis: Result Tracking Backend***

After a worker finishes processing a task, it stores the result and status (SUCCESS, FAILURE, or RETRY) in Redis. Redis serves as a fast, in-memory database that holds the task metadata under unique keys tied to the task_id. Flask can later query Redis using AsyncResult(task_id) to retrieve this data and update the user.

***7. UI Feedback:***

Finally, the frontend periodically polls the backend using the task_id to check the task’s status. Once Redis indicates that the task is complete, Flask fetches the result and returns it to the UI. The user sees a confirmation message or the processed output (e.g., reversed string or sentiment result). This feedback loop ensures the user is kept informed without blocking the main thread.


## Client Interaction Flow

<img src="assets/Flow.svg" alt="Implementation Diagram" width="1000">




## 📁 Project Structure

```
async-tasks/
│
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── celeryconfig.py      # Celery broker/backend configs
│   ├── routes.py            # Routes for UI + task handling
│   ├── tasks.py             # Celery tasks
│   ├── templates/           # Jinja2 HTML UI (index.html)
│   └── static/              # CSS, images, icons
│
├── Dockerfile               # Docker image setup
├── docker-compose.yml       # Multi-service Docker config
├── requirements.txt         # Python dependencies
├── run.py                   # Flask run entry
├── start.sh / start.ps1     # Quick Docker starter script

```



---

## Step-by-Step Setup

### 1️⃣ Clone the Repo and Navigate

```bash
git clone https://github.com/MD-Junayed000/async-tasks.git
cd async-tasks
cd Lab-1-Async-Tasks/Async-tasks
```

### 2️⃣ Start Services via Docker

```bash
docker-compose up --build
```



## 🌐 URLs & Ports

| Service        | URL                                              |
| -------------- | ------------------------------------------------ |
| Flask UI       | [http://localhost:5000](http://localhost:5000)   |
| RabbitMQ Admin | [http://localhost:15672](http://localhost:15672) |
| Flower Monitor | [http://localhost:5555](http://localhost:5555)   |



## Available Tasks

<div align="center">

| Task Type        | Description                           |
| ---------------- | ------------------------------------- |
| **Send Email**   | Simulates sending an email (w/ retry) |
| **Reverse Text** | Reverses any string                   |
| **Sentiment**    | Fake sentiment analysis on input text |

</div>

Each task returns a `Task ID` and status message ✅/❌.


---

## Poridhi Lab Setup
1. Access the application through load balancer:
At first we load the system following the instructions as in local machine and checking if all the ports are forwarded![image](https://github.com/user-attachments/assets/7e400c90-6b9e-4787-8416-12f10e29657c)



2. Configure IP and port:
- Get IP from eth0 using `ifconfig`

<div align="center">
  <img src="https://github.com/user-attachments/assets/c007ea7b-90ba-4270-a214-0e7b24545a1a" alt="WhatsApp Image 2025-06-03 at 15 58 00_f2d59dd0" width="600">
</div>

- Use application port from Dockerfile



3. Create load balancer and configure with your application's IP and port in Poridhi lab:

<div align="center">
  <img src="https://github.com/user-attachments/assets/aec14ae4-a1d6-405b-aa52-e710c5a9ece5" alt="Screenshot 2025-06-03 155900" width="600">
</div>

![image](https://github.com/user-attachments/assets/f7786750-1b00-4e37-86a1-34744d5b7cb4)

---
## Appication
### API Endpoints
**Submit a Task:** Submit any sorts of task like Email,Reverse text proessing,Sentiment analysis if text contain 'good'keywords.If 'fail' keyword in email receipent,it will raise error and will retry max 3 times then discarded.
Domain name for a load balancer in the Poridhi lab environment (For 5000 port):https://67aa3ccddb2c69e7e975ceff-lb-803.bm-southeast.lab.poridhi.io/
   
![Screenshot 2025-06-03 192518](https://github.com/user-attachments/assets/6054e0c2-23f9-4f16-8fd2-e99298c52616)


###  Task Monitoring with Flower

 Open the load balancer for port 5555 in the poridhi lab environment:https://67aa3ccddb2c69e7e975ceff-lb-751.bm-southeast.lab.poridhi.io/tasks

  ![Screenshot 2025-06-03 192629](https://github.com/user-attachments/assets/2dbf9954-abf7-4611-af9f-8e9be87efc2b)

* View task history, retries, failures
* Inspect live workers and system load

### RabbitMQ Management UI
Default credentials: guest/guest
-Monitor queues, exchanges, and connections
![Screenshot 2025-06-03 192604](https://github.com/user-attachments/assets/66837fde-a699-4a30-afab-009b97812658)


### Error Handling & Retries
>Email task uses self.retry() with max_retries=3

>If task fails, it's requeued

>Redis tracks the task state:

* PENDING, SUCCESS, RETRY, FAILURE
![Screenshot 2025-06-03 192859](https://github.com/user-attachments/assets/c33a9312-de04-4305-b0d6-40a9be625430)


> inspect it using:

```bash
docker exec -it async-tasks-redis-1 redis-cli
> KEYS *
> GET celery-task-meta-xxxxxxx
```


###  Use Postman for Submissions

Example JSON for email:

```json
{
  "form_type": "email",
  "recipient": "someone@example.com",
  "subject": "Greetings",
  "body": "Hello from Flask"
}
```

---
## ⚠️ Common Issues & Fixes

| Problem                 | Fix                                    |
| ----------------------- | -------------------------------------- |
| Task not completing     | Check RabbitMQ & Celery logs           |
| Task stuck in `PENDING` | Check Redis config or broker queue     |
| No Redis output         | Use `AsyncResult().get()` or API fetch |
| UI not showing output   | Ensure sessions are set up correctly   |




##  Concepts Implemented

* Direct exchange with `celery_see` queue
* Multi-worker concurrency with `--concurrency=4`
* Flask session flash for notifications
* Redis result tracking via `AsyncResult`
* Queue retry using `self.retry()`


# Async Tasks Dashboard

> **Rather than doing those tasks immediately (and potentially blocking your web server), you hand them off to a background worker via RabbitMQ. You use Redis to track each job’s status (“pending,” “completed,” etc.).**

---

## 🌟 Overview

A minimal demo illustrating how to:

* Offload long‑running or blocking work (text reversal, sentiment analysis, email sending) to background workers.
* Use **RabbitMQ** as a reliable message broker.
* Use **Redis** for job metadata storage and **Pub/Sub** for real‑time updates.
* Use **Socket.IO** to push live status to the browser.

This architecture keeps your Express API fast and responsive, while workers process tasks in parallel and report progress.

---

## 🏛 System Architecture

![System Architecture](./architecture.png)

1. **Browser → Express**
   User submits a form (`Reverse`, `Analyze`, or `Send Email`).
2. **Express → Redis Pub/Sub**

   * `HSET task:<id> status=pending`
   * `PUBLISH task_updates { id, status:"pending", … }`
3. **Express → RabbitMQ**

   * `ch.sendToQueue("tasks", { id, type, payload })` to enqueue the job.
4. **Redis Pub/Sub → Browser (Socket.IO)**
   Express re‑emits the `task_updates` event over WebSocket so the UI shows **pending** immediately.
5. **RabbitMQ → Worker**
   One of the worker processes pulls the next message off the **tasks** queue (`ch.consume`) and begins execution.
6. **Worker → Redis Pub/Sub**

   * On start: `PUBLISH { status:"started" }`
   * On completion/failure:

     * `HSET task:<id> status=<completed|failed>, result=<…>`
     * `PUBLISH { status:"completed"|"failed", result }`
7. **Redis Pub/Sub → Browser (Socket.IO)**
   Express pushes these updates to the UI in real time.

> **Scale:** With `docker-compose up --scale worker=4`, you run 4 identical worker processes. RabbitMQ will distribute tasks round‑robin, and with `ch.prefetch(1)` each worker has at most **one** un‑acked message at a time.

---

## ⚙️ Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/async-tasks-dashboard.git
   cd async-tasks-dashboard
   ```
2. **Build & run**

   ```bash
   docker-compose build api worker
   docker-compose up
   ```
3. **Open your browser**

   * Express UI:  `http://localhost:5000`
   * RabbitMQ Management: `http://localhost:15672`
   * Redis Commander:      `http://localhost:8081`

**Scale workers**:

```bash
docker-compose up --scale worker=4
```

---

## 📁 File Structure

```
├── docker-compose.yml      # defines api, worker, rabbitmq, redis, redis-commander
├── Dockerfile              # Node.js container setup
├── index.js                # Express + Socket.IO + RabbitMQ producer
├── worker.js               # RabbitMQ consumer, runs tasks.js handlers
├── tasks.js                # Task handlers: reverse, sentiment, send email
├── package.json
├── views/
│   └── index.ejs           # EJS template for UI
└── public/
    └── css/style.css       # Styling
```

---

## 🚀 How It Works

### 1. Express API (index.js)

* Hosts a simple web UI.
* On form POST:

  1. Generates a `UUID` for the task.
  2. Stores `{ status: "pending", payload }` in Redis.
  3. Publishes a `pending` event on Redis Pub/Sub.
  4. Enqueues the job in RabbitMQ (`tasks` queue).
  5. For quick tasks (reverse, sentiment), polls Redis up to 10s to inline the result.

### 2. Worker (worker.js)

* Runs as a separate Node.js process (`npm run worker`).
* Connects to RabbitMQ & Redis.
* `ch.prefetch(1)` → only 1 un‑acked message at a time.
* `ch.consume("tasks", …)` pulls jobs.
* For each message:

  1. Publishes `started` to Redis Pub/Sub.
  2. Executes the matching handler in `tasks.js`.
  3. Stores final status+result in Redis.
  4. Publishes `completed` or `failed` event.
  5. Acknowledges (`ack`) or dead‑letters on repeated failure.

### 3. Real‑time Updates (Socket.IO)

* Express subscribes to `task_updates` channel.
* On every update, re‑emits via WebSocket to the browser.
* UI shows live task status and final results.

---

## 🔑 Key Patterns

### `prefetch(1)` → One‑at‑a‑time per worker

* Ensures fair dispatch across N workers.
* Prevents a single worker from getting overloaded.

### Resilience

* Un‑acked messages are re‑queued if a worker dies before ACK.
* Guarantees **at‑least‑once** delivery.

### Horizontal Scaling

* Each Node.js worker is single‑threaded.
* Run multiple worker processes to use more CPU cores:

  ```bash
  ```

docker-compose up --scale worker=4

```

---

🎉 **Enjoy your async, scalable task pipeline!**

```

# Async-Node: Asynchronous Task Processing with Node.js, RabbitMQ & Redis

A demonstration project showing how to offload work from an Express API into background workers using RabbitMQ, track progress in Redis, and stream live updates to the browser via Socket.IO.

---

## Table of Contents

* [Features](#features)
* [Architecture](#architecture)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Usage](#usage)
* [Scaling Workers](#scaling-workers)
* [Project Structure](#project-structure)
* [File Descriptions](#file-descriptions)
* [License](#license)

---

## Features

* **Express API** to submit tasks via HTTP forms
* **RabbitMQ** as a durable work queue with dead-lettering and retry logic
* **Workers** that consume tasks, process them (`send_email_task`, `reverse_text_task`, `fake_sentiment_analysis`), and report status
* **Redis** as a fast key/value store and pub/sub channel to persist task state and broadcast updates
* **Socket.IO** to stream real-time progress (pending, started, completed, failed) back to the browser
* **Redis Commander** and **RabbitMQ Management UI** for manual inspection

---

## Architecture

```
Browser (UI)
    │
    ├─ POST /        → Express API  → Redis (HSET task:ID, PUBLISH pending)
    │                    │
    │                    └─ sendToQueue → RabbitMQ "tasks"
    │
    ├─ WebSocket ←────────────────── Redis Pub/Sub "task_updates"
    │
Worker(s)
    ├─ AMQP consume(tasks) ← RabbitMQ
    ├─ HSET task:ID status=started → Redis
    ├─ run handler(payload) → result
    ├─ HSET task:ID status=result → Redis
    ├─ PUBLISH "task_updates" → Redis
    └─ ack/nack/retry → RabbitMQ
```

---

## Prerequisites

* Docker & Docker Compose
* Node.js (for local development without Docker)

---

## Installation

1. **Clone repository**

   ```bash
   git clone https://github.com/your-username/async-node.git
   cd async-node
   ```

2. **Build & start services**

   ```bash
   docker-compose build api worker
   docker-compose up
   ```

3. **Access UIs**

   * API + UI:  `http://localhost:5000`
   * RabbitMQ Management: `http://localhost:15672` (user: `guest`)
   * Redis Commander:       `http://localhost:8081`

---

## Usage

1. Navigate to `http://localhost:5000` in your browser.
2. Fill out any form:

   * **Send Email** (will simulate success/failure)
   * **Reverse Text**  (quick result embedded)
   * **Sentiment Analysis** (quick result embedded)
3. Inspect live task state in Redis Commander under keys `task:<id>`.
4. Inspect RabbitMQ queue depth in RabbitMQ Management UI.

---

## Scaling Workers

To run multiple workers for parallel processing:

```bash
docker-compose up --scale worker=4
```

Each of the 4 worker containers will `prefetch(1)` message at a time. RabbitMQ round‑robins tasks to each **idle** worker.  If one worker dies or crashes, its unacknowledged message is automatically requeued.

---

## Project Structure

```
async-node/
├── Dockerfile            # Node.js image definition
├── docker-compose.yml    # Multi-service setup
├── package.json          # NPM dependencies & scripts
├── index.js              # Express API + RabbitMQ producer + Redis pub/sub
├── worker.js             # RabbitMQ consumer + task execution + Redis updates
├── tasks.js              # Business logic task handlers
├── views/
│   └── index.ejs         # EJS template for forms & results
└── public/css/
    └── style.css         # Basic styling
```

---

## File Descriptions

* **index.js**

  * Sets up Express + EJS views + static assets
  * Connects to Redis for `HSET` and `PUBLISH` on `task_updates`
  * Connects to RabbitMQ, declares `tasks` queue & DLX
  * `POST /` enqueues new tasks and (for quick tasks) polls Redis for results to render inline

* **worker.js**

  * Connects to RabbitMQ, prefetches 1 message per worker
  * `consume('tasks')`, for each message:

    1. Publish `started` to Redis pub/sub
    2. Run handler from `tasks.js`
    3. HSET final `status` & `result`
    4. Publish `completed`/`failed`
    5. Ack or retry/nack according to attempts
    6. Check queue length and publish on `queue_length`

* **tasks.js**

  * `send_email_task`, `reverse_text_task`, `fake_sentiment_analysis`
  * Each simulates work with a `sleep(500)`
  * Reverse and sentiment return quick results for inline display

* **views/index.ejs**

  * Bootstrap‑based form layout
  * Shows inline results for quick tasks
  * (Live Chart removed—results now static)

* **docker-compose.yml**

  * Services: `api`, `worker`, `rabbitmq`, `redis`, `redis-commander`
  * Declares dependencies and port mappings

* **Dockerfile**

  * `FROM node:18-alpine`, installs dependencies, copies code

---

## License

This project is released under the MIT License. Feel free to adapt and extend!


