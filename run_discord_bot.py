"""
Discord Bot Runner Script

Simple script to start the Career Coach Discord Bot with proper error handling
and status reporting.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    expected_files = ['src/discord_bot.py', 'requirements.txt', '.env.example']
    
    missing_files = []
    for file in expected_files:
        if not (current_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print(f"💡 Make sure you're in the project root directory")
        return False
    
    # Check if .env file exists
    if not (current_dir / '.env').exists():
        print("⚠️  No .env file found")
        print("💡 Create .env file with your Discord bot token:")
        print("   DISCORD_BOT_TOKEN=your_token_here")
        print("   LLM_PROVIDER=ollama")
        return False
    
    print("✅ All requirements met")
    return True


def check_ollama():
    """Check if Ollama is running."""
    print("🔍 Checking Ollama status...")
    
    try:
        result = subprocess.run(
            ['curl', '-s', 'http://localhost:11434/api/version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Ollama is running")
            return True
        else:
            print("⚠️  Ollama might not be running")
            print("💡 Start Ollama: ollama serve")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Could not check Ollama status")
        print("💡 Make sure Ollama is installed and running: ollama serve")
        return False


def start_discord_bot():
    """Start the Discord bot."""
    print("🚀 Starting Discord bot...")
    print("-" * 40)
    
    try:
        # Start the bot
        process = subprocess.run([
            sys.executable, '-m', 'src.discord_bot'
        ], cwd=Path.cwd())
        
        return process.returncode
        
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        return 1


def main():
    """Main function."""
    print("🤖 DISCORD BOT RUNNER - Career Coach LLM Agent")
    print("=" * 60)
    print()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed")
        return 1
    
    # Check Ollama (optional but recommended)
    ollama_running = check_ollama()
    if not ollama_running:
        choice = input("\n❓ Continue without Ollama? (y/n): ").lower().strip()
        if choice != 'y':
            print("💡 Start Ollama first: ollama serve")
            return 1
    
    print("\n🎯 Bot Configuration:")
    print("   • Discord integration: Enabled")
    print("   • Natural language processing: Enabled")
    print("   • Career analysis: Enabled")
    print("   • Job matching: Enabled")
    print("   • Resume review: Enabled")
    print()
    
    # Start bot
    print("🔄 Starting bot... (Press Ctrl+C to stop)")
    print("📱 Once started, test with the discord_test_script.py")
    print()
    
    return start_discord_bot()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)