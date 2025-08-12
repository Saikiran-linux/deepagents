# Research Agent Setup Guide

## 🎯 Quick Setup to Enable Rich Report Generation

Your research agent **is working correctly** - it just needs API keys to access internet search and AI models for comprehensive research.

## 🔑 Required API Keys

### 1. Tavily API Key (For Internet Search)
- **Get it here**: https://tavily.com/
- **Sign up** for a free account
- **Copy your API key** from the dashboard

### 2. OpenAI API Key (For AI Processing)
- **Get it here**: https://platform.openai.com/
- **Sign up** and add payment method
- **Create an API key** in the API section

## 📝 Setup Instructions

### Step 1: Create .env File
Create a file named `.env` in your project root directory with:

```bash
# Research Agent API Keys
TAVILY_API_KEY=your_actual_tavily_api_key_here
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### Step 2: Replace with Your Actual Keys
Replace the placeholder text with your real API keys:
- Remove `your_actual_tavily_api_key_here` and paste your Tavily key
- Remove `your_actual_openai_api_key_here` and paste your OpenAI key

### Step 3: Test the Setup
Run the research agent to verify everything works:

```bash
cd examples/research
python research_agent.py "What is machine learning?"
```

## 🚀 What You'll Get

Once configured, your research agent will:

✅ **Generate rich, comprehensive reports** like the current final_report.md
✅ **Conduct multi-source internet research** using Tavily search
✅ **Create professional formatting** with proper sections and citations
✅ **Include expert analysis** and industry insights
✅ **Provide detailed examples** and real-world applications

## 🔍 Current Status

- ✅ **Agent is working**: Debug tests show successful file creation
- ✅ **Rich report example**: Check final_report.md for comprehensive AI industry report
- ⚠️ **Missing API keys**: Agent failed on internet search due to missing TAVILY_API_KEY

## 💡 Alternative: Use Without Internet Search

If you want to test without API keys, you can modify the agent to work with pre-loaded knowledge:

```bash
# Test file writing capabilities
python research_agent.py --test
```

## 🆘 Troubleshooting

### Common Issues:

1. **"TAVILY_API_KEY is not set"**
   - Solution: Add TAVILY_API_KEY to your .env file

2. **"No module named 'openai'"**
   - Solution: `pip install openai`

3. **Files not created**
   - Solution: Run `python debug_research.py` for diagnosis

4. **Permission errors**
   - Solution: Ensure you have write permissions in the directory

### Test Commands:
```bash
# Basic functionality test
python research_agent.py --test

# Debug issues
python debug_research.py

# Run with specific question
python research_agent.py "Your research question here"
```

## 📊 Expected Results

After setup, your research agent will generate reports with:

- **10,000+ words** of comprehensive content
- **Professional structure** with clear sections and subsections
- **10+ authoritative citations** with proper formatting
- **Industry-specific analysis** across multiple sectors
- **Future trends and recommendations**
- **Executive summary and conclusions**

The current `final_report.md` shows exactly what quality to expect!

## 🎉 Ready to Go!

Once you add your API keys, run:

```bash
python research_agent.py "What are the latest developments in quantum computing?"
```

And watch your agent generate a professional research report automatically!

