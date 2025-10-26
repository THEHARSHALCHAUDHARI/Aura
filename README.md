# Aura: The Contextual AI Assistant

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Aura** is a next-generation, open-source assistive technology project. It uses a modern, scalable stack to provide a real-time contextual AI assistant for individuals who are blind or have low vision.

This system is not just a screen reader; it's a real-world copilot that can see, hear, remember, and connect the user with a sighted assistant when needed.

---

### 🚀 Key Features

* **Conversational AI:** Human-like, real-time voice conversations powered by **Vapi**.
* **Real-Time Context:** Uses live video, GPS, and sensor data to understand the user's environment.
* **Hybrid Computer Vision:** Leverages **OpenCV** for fast, efficient, on-device (or server-side) pre-processing, object detection, and analysis before sending data to the cloud AI.
* **5-Minute Memory:** A robust video pipeline archives the user's stream to **S3**, allowing them to ask questions about the recent past ("What did I just put down?").
* **Remote Sighted Assistance:** A secure web portal for family or friends to log in, see the user's live feed, and provide direct audio assistance.
* **Scalable by Design:** Built on a robust, serverless stack designed to scale from one user to thousands.

---

### 🛠️ Tech Stack & Architecture

This project is a high-performance **[Turborepo](https://turbo.build/repo)** monorepo.

Using a monorepo allows us to manage all our code in a single repository while sharing code, types, and configurations across applications.

* **Monorepo:** **Turborepo**
* **Voice AI:** **Vapi** (for real-time, human-like voice)
* **Core AI:** **OpenAI (GPT-4o)** for multimodal vision and reasoning.
* **Computer Vision:** **OpenCV** (for real-time video processing and analysis)
* **Authentication:** **Clerk** (for both mobile and web)
* **Database:** **Supabase** (Postgres DB, Auth integration, Edge Functions)
* **Web Portal (`apps/web`):** **Next.js** & Tailwind CSS
* **Mobile App (`apps/mobile`):** **React Native (Expo)**
* **Video Ingest Service (`apps/ingest`):** A **Node.js (Fastify/Express)** service to receive the ESP32-CAM stream, process frames with OpenCV, and upload to S3.
* **Real-time Data:** **Redis** (for GPS/sensor Pub/Sub)
* **Video Storage:** **Amazon S3** (for the 5-minute rolling video buffer)
* **Hardware:** **ESP32-CAM** & **ESP8266/LiDAR**

---

### 📦 Project Structure

The monorepo contains `apps` (our user-facing applications and services) and `packages` (shared code).

```
/
├── apps/
│   ├── mobile/     # React Native (Expo) app for the user
│   ├── web/        # Next.js portal for sighted assistants
│   ├── docs/       # Next.js docs site (guides, API, etc.)
│   └── ingest/     # Node.js service for video/OpenCV processing
│
├── packages/
│   ├── db/         # Supabase client, schema, and RLS policies
│   ├── ui/         # Shared React components (buttons, etc.)
│   └── config/     # Shared ESLint, TypeScript configs
│
└── package.json    # Root package.json
└── turbo.json      # Turborepo pipeline configuration
```