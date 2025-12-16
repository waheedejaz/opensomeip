# CMake Build System

CMake-based build system for the SOME/IP stack, designed for cross-platform development with optional safety-oriented compilation settings (non-certified).

## Overview

The CMake build system provides:
- **Cross-platform builds** for Linux, Windows, and embedded targets
- **Safety-oriented compilation options** with MISRA and CERT compliance flags
- **Modular configuration** for different deployment scenarios
- **Dependency management** and external library integration
- **Testing integration** with automated test execution

## Key Features

### Safety-Oriented Build Options (non-certified)
- **MISRA C++ compliance** flags and checking
- **CERT C++ secure coding** standard enforcement
- **ASIL classification** specific build configurations (configuration only; no certification implied)
- **Static analysis** tool integration
- **Code coverage** measurement for safety validation

### Build Configurations
- **Debug**: Development with full debugging support
- **Release**: Optimized production builds
- **Safety**: Builds with additional safety checks (non-certified)
- **Coverage**: Builds with code coverage instrumentation

## Directory Structure

### CMake Modules
- **FindXXX.cmake**: External dependency detection
- **Safety.cmake**: Safety-critical build configuration
- **Testing.cmake**: Test integration and execution
- **Packaging.cmake**: Binary package generation

### Platform Support
- **Linux.cmake**: Linux-specific configuration
- **Windows.cmake**: Windows-specific configuration
- **Embedded.cmake**: Embedded target configurations
- **CrossCompile.cmake**: Cross-compilation support

## Usage

### Basic Build
```bash
mkdir build && cd build
cmake ..
make
```

### Safety-Oriented Build
```bash
mkdir build && cd build
cmake .. -DSAFETY_LEVEL=ASIL_B -DSTATIC_ANALYSIS=ON
make
```

### Cross-Compilation
```bash
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/toolchains/arm64.cmake
make
```

## Build Options

### Safety Options
- `SAFETY_LEVEL`: ASIL_A, ASIL_B, ASIL_C, ASIL_D (configuration only; no certification implied)
- `MISRA_COMPLIANCE`: Enable MISRA C++ rule checking
- `CERT_COMPLIANCE`: Enable CERT C++ rule checking
- `STATIC_ANALYSIS`: Enable static analysis tools

### Feature Options
- `BUILD_TESTS`: Build test executables
- `BUILD_EXAMPLES`: Build example programs
- `BUILD_TOOLS`: Build development tools
- `ENABLE_SD`: Enable Service Discovery
- `ENABLE_TP`: Enable Transport Protocol

### Platform Options
- `TARGET_PLATFORM`: linux, windows, embedded
- `CROSS_COMPILE`: Enable cross-compilation
- `TOOLCHAIN_PATH`: Path to cross-compiler toolchain

## Safety Considerations (non-certified)

### Compilation Flags
- **Warning Levels**: Maximum warning detection (-Wall, -Wextra, -Wpedantic)
- **Error Handling**: Treat warnings as errors in safety builds
- **Optimization**: Controlled optimization for safety-oriented code
- **Debugging**: Full debug information preservation

### Code Quality
- **Static Analysis**: Integration with cppcheck, clang-tidy
- **MISRA Checking**: Automated MISRA rule verification
- **CERT Checking**: CERT secure coding standard compliance
- **Code Coverage**: MC/DC coverage for safety-related code

## Dependencies

### Required Dependencies
- **CMake 3.20+**: Build system
- **C++17 Compiler**: GCC 9+, Clang 10+, MSVC 2019+
- **Boost 1.70+**: Utility libraries
- **googletest**: Unit testing framework

### Optional Dependencies
- **Doxygen**: Documentation generation
- **cppcheck**: Static analysis
- **clang-tidy**: Code quality checking
- **lcov**: Code coverage reporting

## Output Structure

### Library Targets
- **someip-core**: Core protocol library
- **someip-transport**: Transport layer library
- **someip-sd**: Service Discovery library
- **someip-tp**: Transport Protocol library
- **someip-serialization**: Serialization library

### Executable Targets
- **tests**: Test executables
- **examples**: Example programs
- **tools**: Development tools

## Integration

### IDE Integration
- **Visual Studio**: Native CMake support
- **CLion**: CMake-based projects
- **VS Code**: CMake Tools extension
- **Eclipse**: CMake CDT integration

### CI/CD Integration
- **GitHub Actions**: Automated builds and tests
- **GitLab CI**: Pipeline integration
- **Jenkins**: Build automation
- **Azure DevOps**: Cloud-based CI/CD

## Troubleshooting

### Common Issues
- **Compiler Compatibility**: Ensure C++17 support
- **Dependency Resolution**: Check Boost installation
- **Cross-Compilation**: Verify toolchain paths
- **Static Analysis**: Install analysis tools

### Debug Builds
```bash
# Verbose build output
make VERBOSE=1

# Single target build
make someip-core

# Clean rebuild
make clean && make
```
