# Examples organized in hierarchical structure
# Each subdirectory contains its own CMakeLists.txt

# Basic Examples
add_subdirectory(basic/hello_world)
add_subdirectory(basic/method_calls)
# add_subdirectory(basic/events)  # Temporarily disabled due to API compatibility issues

# Advanced Examples
add_subdirectory(advanced/complex_types)
add_subdirectory(advanced/large_messages)
add_subdirectory(advanced/multi_service)

# All examples have been migrated to hierarchical structure
# Legacy examples removed - use basic/ and advanced/ subdirectories
