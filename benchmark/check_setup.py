"""
Benchmark Tool - Setup Checker
Verifies all dependencies and files are ready for benchmarking.
"""

import sys
from pathlib import Path

def check_setup():
    """Check if benchmark tool is properly set up"""
    
    print("=" * 80)
    print("🔍 Benchmark Tool Setup Checker")
    print("=" * 80)
    print()
    
    errors = []
    warnings = []
    
    # 1. Check Python version
    print("1️⃣ Checking Python version...")
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    else:
        errors.append("Python 3.8+ required")
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.8+)")
    
    # 2. Check required packages
    print("\n2️⃣ Checking required packages...")
    packages = ['pandas', 'matplotlib', 'seaborn', 'prettytable', 'numpy']
    
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"   ✅ {pkg}")
        except ImportError:
            errors.append(f"Package '{pkg}' not installed")
            print(f"   ❌ {pkg} - NOT INSTALLED")
    
    # 3. Check benchmark files
    print("\n3️⃣ Checking benchmark files...")
    benchmark_dir = Path(__file__).parent
    required_files = [
        'benchmark_calculation.py',
        'quick_demo.py',
        'sample_output.py',
        'requirements.txt',
        'README.md',
        'USAGE.md'
    ]
    
    for file in required_files:
        file_path = benchmark_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            warnings.append(f"File '{file}' missing")
            print(f"   ⚠️ {file} - MISSING")
    
    # 4. Check level files
    print("\n4️⃣ Checking level files...")
    project_root = benchmark_dir.parent
    levels_dir = project_root / "assets" / "levels"
    
    if levels_dir.exists():
        print(f"   ✅ Levels directory: {levels_dir}")
        
        level_files = list(levels_dir.glob("*.slc"))
        if level_files:
            print(f"   ✅ Found {len(level_files)} level files:")
            for lf in level_files:
                print(f"      • {lf.name}")
        else:
            warnings.append("No .slc level files found")
            print(f"   ⚠️ No .slc files in {levels_dir}")
    else:
        errors.append(f"Levels directory not found: {levels_dir}")
        print(f"   ❌ Levels directory not found")
    
    # 5. Check sokoban_bot
    print("\n5️⃣ Checking Sokoban modules...")
    src_modules = [
        'src.levels.level',
        'src.game_manager',
        'src.algorithms.sokoban_bot'
    ]
    
    sys.path.insert(0, str(project_root))
    
    for mod in src_modules:
        try:
            __import__(mod)
            print(f"   ✅ {mod}")
        except ImportError as e:
            errors.append(f"Cannot import '{mod}': {e}")
            print(f"   ❌ {mod} - IMPORT ERROR")
    
    # 6. Test load Cosmonotes
    print("\n6️⃣ Testing Cosmonotes.slc load...")
    cosmonotes = levels_dir / "Cosmonotes.slc"
    
    if cosmonotes.exists():
        print(f"   ✅ Cosmonotes.slc exists")
        
        try:
            from src.levels.level import LevelCollection
            collection = LevelCollection()
            if collection.load_from_slc(str(cosmonotes)):
                print(f"   ✅ Loaded {len(collection.levels)} levels")
            else:
                warnings.append("Failed to parse Cosmonotes.slc")
                print(f"   ⚠️ Failed to parse file")
        except Exception as e:
            warnings.append(f"Error loading Cosmonotes: {e}")
            print(f"   ⚠️ Error: {e}")
    else:
        errors.append("Cosmonotes.slc not found")
        print(f"   ❌ Cosmonotes.slc not found")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    if not errors and not warnings:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 Ready to run benchmarks:")
        print("   • Sample output:  uv run python benchmark\\sample_output.py")
        print("   • Quick demo:     uv run python benchmark\\quick_demo.py")
        print("   • Full benchmark: uv run python benchmark\\benchmark_calculation.py")
        return True
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    
    if warnings:
        print(f"\n⚠️ WARNINGS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    if errors:
        print("\n💡 To fix errors:")
        print("   1. Install missing packages:")
        print("      uv add pandas matplotlib seaborn prettytable numpy")
        print("   2. Make sure you're in the Sokoban project directory")
        print("   3. Verify level files exist in assets/levels/")
        return False
    else:
        print("\n💡 Warnings are non-critical. You can proceed with caution.")
        return True

if __name__ == "__main__":
    success = check_setup()
    sys.exit(0 if success else 1)
