# File Server Management - Frontend

Modern web interface for managing multi-protocol file servers.

## 🚀 Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **TanStack Query** - Server state management
- **Zustand** - Client state management  
- **Axios** - HTTP client with auto token refresh

## 📦 Features

### ✅ Implemented
- 🔐 **Authentication** - JWT login with auto token refresh
- 📊 **Dashboard** - Overview with stats and protocol status
- 🖥️ **Protocol Management** - Install, start, stop protocols (FTP, SFTP, SMB, S3)
- 👥 **User Management** - CRUD operations for user accounts
- 🎨 **Responsive UI** - Mobile-friendly sidebar navigation
- 🌗 **Dark Mode** - Theme support (CSS vars ready)

### 🟡 Stub Pages (Coming Soon)
- 📁 Shared Paths
- 💾 Quotas & Usage
- 📝 Logs & Audit Trail
- ⚙️ Settings

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev

# Open http://localhost:3000
```

## 🔑 Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Change immediately in production!**

## 📁 Project Structure

```
frontend/
├── app/
│   ├── dashboard/           # Protected dashboard routes
│   │   ├── layout.tsx       # Sidebar navigation
│   │   ├── page.tsx         # Dashboard overview
│   │   ├── protocols/       # Protocol management
│   │   ├── users/           # User management
│   │   ├── paths/           # Shared paths (stub)
│   │   ├── quotas/          # Quotas (stub)
│   │   ├── logs/            # Logs (stub)
│   │   └── settings/        # Settings (stub)
│   ├── login/               # Login page
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Root redirect
│   ├── providers.tsx        # TanStack Query provider
│   └── globals.css          # Global styles
├── components/
│   └── ui/                  # Reusable UI components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── table.tsx
├── lib/
│   ├── api.ts               # API client with interceptors
│   ├── store.ts             # Zustand auth store
│   └── utils.ts             # Utility functions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🔌 API Integration

The frontend connects to the FastAPI backend via:

- **Base URL**: `NEXT_PUBLIC_API_URL` (default: `http://localhost:8000`)
- **Auto Token Refresh**: Axios interceptor handles JWT expiration
- **State Management**: TanStack Query for server state caching

### API Endpoints Used

- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `GET /api/auth/me` - Current user info
- `GET /api/protocols` - List protocols
- `POST /api/protocols/{name}/install` - Install protocol
- `POST /api/protocols/{name}/start` - Start service
- `POST /api/protocols/{name}/stop` - Stop service
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `DELETE /api/users/{id}` - Delete user

## 🎨 UI Components

All UI components use:
- **CVA** (Class Variance Authority) for type-safe variants
- **Tailwind CSS** for styling
- **CSS Variables** for theming
- **Responsive Design** - Mobile-first approach

## 🚀 Deployment

### Production Build

```bash
npm run build
npm start
```

### Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_APP_NAME=File Server Management
```

### Docker

Use the included `docker-compose.yml` in the root directory to deploy the complete stack.

## 📝 Notes

- **Auto-refresh**: Protocol status updates every 5 seconds
- **Loading States**: All actions show loading indicators
- **Error Handling**: User-friendly error messages
- **Type Safety**: Full TypeScript coverage
- **Optimistic UI**: Immediate feedback on user actions

## 🔗 Related

- [Backend API Documentation](../README.md)
- [Installation Guide](../scripts/install.sh)
- [Protocol Installers](../backend/installers/)
