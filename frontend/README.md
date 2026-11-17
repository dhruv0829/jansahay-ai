# JanSahay Frontend

The frontend for **JanSahay** is built with **React 18**, **Vite**, **Tailwind CSS**, **React Router**, and **Lucide React**.

## Key Design Principles

- **Civic-Tech Visual Language**: Deep Teal (`#0F766E`), Trustworthy Blue (`#2563EB`), Slate backgrounds (`#F8FAFC`), crisp 1px borders, Inter typography.
- **Explainable Recommendation Cards**: Shows exact match percentages, status badges (*Likely Eligible*, *Possibly Eligible*, *Not Eligible*), and bullet points detailing why criteria matched.
- **Multilingual Support**: Real-time interface language switcher for English, Hindi (हिन्दी), and Marathi (मराठी).
- **Web Speech API Voice UI**: Voice microphone interaction with graceful fallback to standard typing.
- **6-Step Guided Onboarding**: Clean, stepwise citizen registration wizard with 1-click demo prefill for presentation speed.

## Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev
```

Frontend will run at `http://localhost:5173`.
