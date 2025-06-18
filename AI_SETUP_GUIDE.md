# 🤖 AI Features Setup Guide

CodeVerse now includes **FREE AI assistance** powered by leading online AI APIs! Get intelligent code hints, problem recommendations, and chat with an AI coding mentor.

## 🌟 Quick Setup (5 minutes)

### Step 1: Get Your FREE API Keys

#### **Option 1: Groq API (Recommended - Super Fast!)**
1. Visit: https://console.groq.com/
2. Sign up with email (no credit card required)
3. Go to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_...`)

**Free Tier:** 14,400 requests/day - Perfect for daily coding practice!

#### **Option 2: Hugging Face (Great Alternative)**
1. Visit: https://huggingface.co/
2. Create free account
3. Go to Settings → Access Tokens
4. Create new token with "Read" permissions
5. Copy the token (starts with `hf_...`)

**Free Tier:** 30,000 requests/month

#### **Option 3: Google Gemini (Powerful)**
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Copy the key

**Free Tier:** 15 requests/minute, 1500/day

### Step 2: Add Keys to Your Project

1. Open `.env` file in your CodeVerse project
2. Replace the placeholder values:

```env
# Replace these with your actual API keys
GROQ_API_KEY=gsk_your_actual_groq_key_here
HUGGINGFACE_API_KEY=hf_your_actual_huggingface_key_here
GEMINI_API_KEY=your_actual_gemini_key_here
```

**Note:** You only need ONE API key to get started! The system will automatically use the available one.

### Step 3: Start Coding with AI! 🚀

1. Restart your Django server: `python manage.py runserver 8001`
2. Visit any problem page
3. Write some code and click **"🤖 AI Hint"**
4. Check out the **AI Dashboard** for recommendations and chat

## ✨ AI Features Available

### 🎯 **Smart Code Hints**
- Get personalized hints based on your current code
- Hints are educational, not full solutions
- Works with Python, Java, C++, JavaScript, Go, and Rust

### 📋 **Problem Recommendations**
- AI analyzes your solved problems
- Suggests next challenges based on your skill level
- Personalized learning path

### 💬 **AI Coding Chat**
- Ask questions about algorithms and data structures
- Get explanations of programming concepts
- 24/7 AI mentor support

### 📊 **Smart Analytics**
- Track your progress
- See success rates
- Get insights on areas to improve

## 🔒 Privacy & Security

- Your code is only sent to AI services when you explicitly request hints
- API keys are stored securely in environment variables
- No data is permanently stored by AI services
- All communication is encrypted (HTTPS)

## 🆓 Cost Breakdown

All features are **100% FREE** with generous limits:

| Service | Free Requests | Perfect For |
|---------|---------------|-------------|
| Groq | 14,400/day | Heavy daily use |
| Hugging Face | 30,000/month | Regular practice |
| Gemini | 1,500/day | Quality insights |

**Example:** With Groq's free tier, you could get 480 AI hints per day!

## 🛠️ Troubleshooting

### "AI service temporarily unavailable"
- Check your API key is correctly set in `.env`
- Ensure you haven't exceeded free tier limits
- Try a different AI service

### "Connection error"
- Check your internet connection
- Verify API keys are valid
- Make sure `.env` file is properly formatted

### Getting started quickly
- Just get a Groq API key (fastest setup)
- Add it to `.env` as `GROQ_API_KEY=your_key_here`
- Restart server and enjoy AI features!

## 🌈 What's Next?

This is just the beginning! Future AI features planned:
- Auto-generated test cases
- Code review and optimization suggestions
- Difficulty prediction for custom problems
- AI-powered debugging assistance

---

**Ready to supercharge your coding practice with AI?** Get your free API key and start coding smarter today! 🚀
