# CampConnect — Backend API 🚀

Welcome to the backend of **CampConnect**, a high-fidelity platform designed to enhance social integration for university students. This API handles authentication, event management, participations, and professional AI-generated poster services.

## 🛠️ Tech Stack
- **FastAPI**: High-performance Python web framework.
- **Supabase**: PostgreSQL database, Authentication, and Storage.
- **Cloudflare Workers AI**: AI-driven image generation (SDXL) for event posters.
- **Pydantic**: Data validation and settings management.

## 🌟 Key Features
- **AI-Powered Posters**: Automated generation of professional event posters using Cloudflare Workers AI.
- **Secure Auth**: Seamless integration with Supabase Auth (JWT).
- **Event Management**: CRUD operations for university activities with category-based filtering.
- **Participant Tracking**: Real-time join/leave functionality for student events.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Cloudflare Account (ID and API Token)
- Supabase Project (URL and Service Key)

### Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables (see `.env.example`).
4. Run the server:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

## 🧪 Documentation
Once the server is running, visit `/docs` for the interactive Swagger UI.

---