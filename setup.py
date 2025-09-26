"""
Hummingbird Monitor - Project Setup Script
"""

import os
import sys
import subprocess
import platform

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception running command: {command}")
        print(f"Exception: {e}")
        return False

def check_python():
    """Check if Python is installed"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"Python version: {result.stdout.strip()}")
        return True
    except:
        print("Python is not installed or not in PATH")
        return False

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"Node.js version: {result.stdout.strip()}")
        return True
    except:
        print("Node.js is not installed or not in PATH")
        return False

def setup_backend():
    """Setup the Python backend"""
    print("\n🐍 Setting up Python backend...")
    
    # Check if we're in the right directory
    if not os.path.exists("backend"):
        print("Error: backend directory not found. Run this script from the project root.")
        return False
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    if not run_command(f"{sys.executable} -m venv backend/venv"):
        return False
    
    # Determine activation script based on OS
    if platform.system() == "Windows":
        activate_script = "backend\\venv\\Scripts\\activate"
        pip_command = "backend\\venv\\Scripts\\pip"
    else:
        activate_script = "source backend/venv/bin/activate"
        pip_command = "backend/venv/bin/pip"
    
    # Install requirements
    print("Installing Python dependencies...")
    if not run_command(f"{pip_command} install -r backend/requirements.txt"):
        return False
    
    # Initialize database
    print("Initializing database...")
    if not run_command(f"{pip_command} install -e .", cwd="backend"):
        # Try alternative approach
        if not run_command(f"{sys.executable} backend/init_db.py"):
            print("Warning: Database initialization failed, but continuing...")
    
    print("✅ Backend setup completed!")
    return True

def setup_frontend():
    """Setup the React frontend"""
    print("\n⚛️ Setting up React frontend...")
    
    # Check if we're in the right directory
    if not os.path.exists("frontend"):
        print("Error: frontend directory not found. Run this script from the project root.")
        return False
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    if not run_command("npm install", cwd="frontend"):
        return False
    
    print("✅ Frontend setup completed!")
    return True

def main():
    """Main setup function"""
    print("🐦 Hummingbird Monitor - Project Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    if not check_python():
        print("❌ Python is required but not found. Please install Python 3.8+")
        return False
    
    if not check_node():
        print("❌ Node.js is required but not found. Please install Node.js 16+")
        return False
    
    print("✅ Prerequisites check passed!")
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed!")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed!")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📖 Next steps:")
    print("1. Start the backend server:")
    if platform.system() == "Windows":
        print("   cd backend && venv\\Scripts\\activate && python run_server.py")
    else:
        print("   cd backend && source venv/bin/activate && python run_server.py")
    
    print("2. Start the frontend server:")
    print("   cd frontend && npm start")
    
    print("\n3. Open your browser to:")
    print("   http://localhost:3000")
    
    print("\n📚 Documentation:")
    print("   - README.md: Complete setup instructions")
    print("   - backend/README.md: Backend API documentation")
    print("   - frontend/setup.md: Frontend setup guide")

if __name__ == "__main__":
    main()
