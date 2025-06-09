#!/usr/bin/env python3
"""
Simple Docker test script to check permissions and build image
"""
import subprocess
import sys
import os

def test_docker_access():
    """Test if Docker is accessible"""
    try:
        result = subprocess.run(['docker', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Docker is accessible")
            return True
        else:
            print("❌ Docker access failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Docker command timed out")
        return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False
    except Exception as e:
        print(f"❌ Docker test failed: {e}")
        return False

def check_image_exists():
    """Check if the VulnScanner image exists"""
    try:
        result = subprocess.run(['docker', 'images', '-q', 'vulnscanner/vulnscanner:latest'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            print("✅ VulnScanner Docker image exists")
            return True
        else:
            print("❌ VulnScanner Docker image not found")
            return False
    except Exception as e:
        print(f"❌ Failed to check image: {e}")
        return False

def build_image():
    """Build the VulnScanner Docker image"""
    print("🔨 Building VulnScanner Docker image...")
    try:
        result = subprocess.run(['docker', 'build', '-t', 'vulnscanner/vulnscanner:latest', '.'], 
                              cwd=os.path.dirname(os.path.abspath(__file__)),
                              timeout=300)
        if result.returncode == 0:
            print("✅ Docker image built successfully")
            return True
        else:
            print("❌ Docker image build failed")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Docker build timed out")
        return False
    except Exception as e:
        print(f"❌ Docker build failed: {e}")
        return False

def test_container_run():
    """Test running the container with --help"""
    print("🧪 Testing container execution...")
    try:
        result = subprocess.run(['docker', 'run', '--rm', 'vulnscanner/vulnscanner:latest', '--help'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Container runs successfully")
            print("📋 Help output preview:")
            print(result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
            return True
        else:
            print("❌ Container execution failed")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Container test failed: {e}")
        return False

def main():
    print("🔍 VulnScanner Docker Test Suite")
    print("=" * 40)
    
    # Test Docker access
    if not test_docker_access():
        print("\n💡 Docker access issue detected!")
        print("To fix Docker permissions, run:")
        print("  sudo usermod -aG docker ${USER}")
        print("Then log out and log back in.")
        return False
    
    # Check if image exists
    if not check_image_exists():
        print("\n🔨 Image not found. Building now...")
        if not build_image():
            return False
    
    # Test container execution
    if not test_container_run():
        return False
    
    print("\n🎉 All tests passed! VulnScanner is ready to use.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 