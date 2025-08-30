# RouteTunnel Frontend

A modern React frontend for the RouteTunnel service, built with TypeScript, Vite, and Tailwind CSS.

## Features

- **Authentication**: Login and registration with form validation
- **Dashboard**: Tunnel management interface
- **Form Validation**: Comprehensive client-side validation using Yup
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **Type Safety**: Full TypeScript support
- **Modern UI**: Clean, accessible interface with Headless UI components

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **React Hook Form** with Yup validation
- **Axios** for API communication
- **Headless UI** for accessible components
- **Heroicons** for icons

## Development

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Setup

1. Install dependencies:
```bash
npm install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_PUBLIC_BASE_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Docker

Build the Docker image:
```bash
docker build -t routetunnel-frontend .
```

Run the container:
```bash
docker run -p 3000:80 routetunnel-frontend
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── auth/           # Authentication components
│   ├── forms/          # Form components
│   └── tunnel/         # Tunnel-related components
├── contexts/           # React contexts
├── lib/                # Utility libraries
├── pages/              # Page components
├── types/              # TypeScript type definitions
└── App.tsx             # Main application component
```

## Form Validation

The application uses comprehensive form validation with the following features:

- **Email validation**: Proper email format checking
- **Password strength**: Minimum requirements with strength indicator
- **Phone number validation**: International format validation
- **Route validation**: Alphanumeric with hyphens and underscores
- **Real-time validation**: Immediate feedback as users type

## Authentication Flow

1. **Registration**: Users can create accounts with email, phone, and password
2. **Login**: Secure authentication with JWT tokens
3. **Token Management**: Automatic token refresh and storage
4. **Protected Routes**: Dashboard requires authentication
5. **Logout**: Secure token cleanup

## API Integration

The frontend communicates with the backend through a centralized API client that handles:

- **Authentication**: Login, registration, token refresh
- **Tunnel Management**: Create, list, and delete tunnels
- **Error Handling**: Consistent error display and handling
- **Request Interceptors**: Automatic token attachment
- **Response Interceptors**: Token refresh on expiration

## Styling

The application uses Tailwind CSS with custom components:

- **Design System**: Consistent colors, spacing, and typography
- **Responsive Design**: Mobile-first approach
- **Accessibility**: WCAG compliant components
- **Dark Mode Ready**: Prepared for future dark mode support

## Contributing

1. Follow the existing code style
2. Add TypeScript types for all new code
3. Include form validation for user inputs
4. Test responsive design on different screen sizes
5. Ensure accessibility compliance