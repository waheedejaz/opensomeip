#include <gtest/gtest.h>
#include "sd/sd_message.h"

using namespace someip::sd;

// Test that demonstrates proper initialization of SD message fields
TEST(SdInitializationTest, AllFieldsProperlyInitialized) {
    // Test ServiceEntry (concrete subclass)
    ServiceEntry service_entry;
    EXPECT_EQ(service_entry.get_type(), EntryType::FIND_SERVICE);
    EXPECT_EQ(service_entry.get_ttl(), 0u);
    EXPECT_EQ(service_entry.get_index1(), 0u);
    EXPECT_EQ(service_entry.get_index2(), 0u);
    EXPECT_EQ(service_entry.get_service_id(), 0u);
    EXPECT_EQ(service_entry.get_instance_id(), 0u);
    EXPECT_EQ(service_entry.get_major_version(), 0u);
    EXPECT_EQ(service_entry.get_minor_version(), 0u);

    // Test SdMessage
    SdMessage message;
    EXPECT_EQ(message.get_flags(), 0u);
    EXPECT_EQ(message.get_reserved(), 0u);
    EXPECT_TRUE(message.get_entries().empty());
    EXPECT_TRUE(message.get_options().empty());

    // Test IPv4EndpointOption (concrete subclass)
    IPv4EndpointOption option;
    EXPECT_EQ(option.get_type(), OptionType::IPV4_ENDPOINT);
    EXPECT_EQ(option.get_length(), 0u);
    EXPECT_EQ(option.get_protocol(), 0u);
    EXPECT_EQ(option.get_ipv4_address(), 0u);
    EXPECT_EQ(option.get_port(), 0u);
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
