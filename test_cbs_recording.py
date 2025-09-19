#!/usr/bin/env python3
"""
Test script for CBS radio recording with Streamlink
Run this to verify the implementation works with CBS streams
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# CBS stream URLs to test
CBS_STREAMS = {
    "CBS 음악FM": "https://m-aac.cbs.co.kr/mweb_cbs939/_definst_/cbs939.stream/chunklist.m3u8",
    "CBS 표준FM": "https://m-aac.cbs.co.kr/mweb_cbs981/_definst_/cbs981.stream/chunklist.m3u8",
    "CBS Joy4You": "https://m-aac.cbs.co.kr/mweb_cbscmc/_definst_/cbscmc.stream/chunklist.m3u8"
}

async def test_streamlink_installation():
    """Test if streamlink is properly installed"""
    try:
        result = await asyncio.create_subprocess_exec(
            "streamlink", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()

        if result.returncode == 0:
            version = stdout.decode().strip()
            print(f"✅ Streamlink installed: {version}")
            return True
        else:
            print(f"❌ Streamlink not working: {stderr.decode()}")
            return False
    except FileNotFoundError:
        print("❌ Streamlink not found. Please install with: pip install streamlink")
        return False

async def test_stream_availability(name, url):
    """Test if a stream URL is available"""
    print(f"Testing {name}...")

    try:
        # Test stream availability (no download)
        result = await asyncio.create_subprocess_exec(
            "streamlink", url, "best", "--stream-url",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()

        if result.returncode == 0:
            direct_url = stdout.decode().strip()
            print(f"  ✅ {name} - Stream available")
            print(f"     Direct URL: {direct_url[:60]}...")
            return True
        else:
            print(f"  ❌ {name} - Stream not available")
            print(f"     Error: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ {name} - Exception: {e}")
        return False

async def test_short_recording(name, url, duration=30):
    """Test short recording (30 seconds) to verify the full pipeline"""
    print(f"Testing {duration}s recording of {name}...")

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_{name.replace(' ', '_')}_{timestamp}.mp3"

    try:
        cmd = [
            "streamlink",
            url,
            "best",
            "--output", output_file,
            "--force",
            "--retry-streams", "3",
            "--retry-max", "5",
            "--ffmpeg-ffmpeg", f"-t {duration}"
        ]

        print(f"  Running: {' '.join(cmd)}")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            # Check if file was created
            if Path(output_file).exists():
                file_size = Path(output_file).stat().st_size
                print(f"  ✅ {name} - Recording successful!")
                print(f"     File: {output_file}")
                print(f"     Size: {file_size:,} bytes")

                # Clean up test file
                Path(output_file).unlink()
                return True
            else:
                print(f"  ❌ {name} - No output file created")
                return False
        else:
            print(f"  ❌ {name} - Recording failed")
            print(f"     Error: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"  ❌ {name} - Exception: {e}")
        return False

async def main():
    """Run all tests"""
    print("🎵 CBS Radio Recording Test")
    print("=" * 50)

    # Test 1: Streamlink installation
    if not await test_streamlink_installation():
        print("\n❌ Streamlink installation test failed. Please install streamlink.")
        sys.exit(1)

    print("\n📡 Testing stream availability...")
    print("-" * 30)

    # Test 2: Stream availability
    available_streams = []
    for name, url in CBS_STREAMS.items():
        if await test_stream_availability(name, url):
            available_streams.append((name, url))

    if not available_streams:
        print("\n❌ No CBS streams are currently available")
        sys.exit(1)

    print(f"\n✅ {len(available_streams)} streams available")

    # Test 3: Short recording test
    print("\n🎙️ Testing recording functionality...")
    print("-" * 40)

    success_count = 0
    for name, url in available_streams[:2]:  # Test first 2 available streams
        if await test_short_recording(name, url):
            success_count += 1

    # Summary
    print("\n📊 Test Results")
    print("=" * 20)
    print(f"✅ Streams available: {len(available_streams)}")
    print(f"✅ Successful recordings: {success_count}")

    if success_count > 0:
        print("\n🎉 CBS radio recording implementation is working!")
        print("   Ready for production use.")
    else:
        print("\n❌ Recording tests failed. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())