/********************************************************************************
 * Copyright (c) 2025 Vinicius Tadeu Zein
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

#include "sd/sd_message.h"
#include "serialization/serializer.h"
#include <algorithm>

namespace someip {
namespace sd {

// SdEntry serialization/deserialization
std::vector<uint8_t> SdEntry::serialize() const {
    std::vector<uint8_t> data;
    data.reserve(16);  // SD entry is 16 bytes

    // Type (1 byte)
    data.push_back(static_cast<uint8_t>(type_));

    // Index 1 (1 byte)
    data.push_back(index1_);

    // Index 2 (1 byte)
    data.push_back(index2_);

    // Number of Options 1 (1 byte) - derived classes will handle
    data.push_back(0);

    // Number of Options 2 (1 byte) - derived classes will handle
    data.push_back(0);

    // Service ID (2 bytes) - derived classes will handle
    data.push_back(0);
    data.push_back(0);

    // Instance ID (2 bytes) - derived classes will handle
    data.push_back(0);
    data.push_back(0);

    // Major Version (1 byte) - derived classes will handle
    data.push_back(0);

    // TTL (4 bytes)
    data.push_back((ttl_ >> 24) & 0xFF);
    data.push_back((ttl_ >> 16) & 0xFF);
    data.push_back((ttl_ >> 8) & 0xFF);
    data.push_back(ttl_ & 0xFF);

    return data;
}

bool SdEntry::deserialize(const std::vector<uint8_t>& data, size_t& offset) {
    if (offset + 16 > data.size()) {
        return false;
    }

    type_ = static_cast<EntryType>(data[offset++]);
    index1_ = data[offset++];
    index2_ = data[offset++];
    offset += 2;  // Skip number of options (handled by SdMessage)

    // Service ID, Instance ID, Major Version, TTL will be handled by derived classes
    return true;
}

// ServiceEntry implementation
std::vector<uint8_t> ServiceEntry::serialize() const {
    std::vector<uint8_t> data = SdEntry::serialize();

    // Override the service ID field (bytes 4-5)
    data[4] = (service_id_ >> 8) & 0xFF;
    data[5] = service_id_ & 0xFF;

    // Override the instance ID field (bytes 6-7)
    data[6] = (instance_id_ >> 8) & 0xFF;
    data[7] = instance_id_ & 0xFF;

    // Override the major version field (byte 8)
    data[8] = major_version_;

    return data;
}

bool ServiceEntry::deserialize(const std::vector<uint8_t>& data, size_t& offset) {
    if (!SdEntry::deserialize(data, offset)) {
        return false;
    }

    if (offset + 9 > data.size()) {
        return false;
    }

    service_id_ = (data[offset] << 8) | data[offset + 1];
    instance_id_ = (data[offset + 2] << 8) | data[offset + 3];
    major_version_ = data[offset + 4];
    ttl_ = (data[offset + 5] << 24) | (data[offset + 6] << 16) |
           (data[offset + 7] << 8) | data[offset + 8];

    offset += 9;
    return true;
}

// EventGroupEntry implementation
std::vector<uint8_t> EventGroupEntry::serialize() const {
    std::vector<uint8_t> data = SdEntry::serialize();

    // Override the service ID field (bytes 4-5)
    data[4] = (service_id_ >> 8) & 0xFF;
    data[5] = service_id_ & 0xFF;

    // Override the instance ID field (bytes 6-7)
    data[6] = (instance_id_ >> 8) & 0xFF;
    data[7] = instance_id_ & 0xFF;

    // Override the major version field (byte 8)
    data[8] = major_version_;

    // Event group ID (bytes 9-10)
    data.push_back((eventgroup_id_ >> 8) & 0xFF);
    data.push_back(eventgroup_id_ & 0xFF);

    return data;
}

bool EventGroupEntry::deserialize(const std::vector<uint8_t>& data, size_t& offset) {
    if (!SdEntry::deserialize(data, offset)) {
        return false;
    }

    if (offset + 11 > data.size()) {
        return false;
    }

    service_id_ = (data[offset] << 8) | data[offset + 1];
    instance_id_ = (data[offset + 2] << 8) | data[offset + 3];
    major_version_ = data[offset + 4];
    ttl_ = (data[offset + 5] << 24) | (data[offset + 6] << 16) |
           (data[offset + 7] << 8) | data[offset + 8];
    eventgroup_id_ = (data[offset + 9] << 8) | data[offset + 10];

    offset += 11;
    return true;
}

// SdOption serialization/deserialization
std::vector<uint8_t> SdOption::serialize() const {
    std::vector<uint8_t> data;

    // Type (1 byte)
    data.push_back(static_cast<uint8_t>(type_));

    // Reserved (1 byte)
    data.push_back(0);

    // Length (2 bytes)
    data.push_back((length_ >> 8) & 0xFF);
    data.push_back(length_ & 0xFF);

    return data;
}

bool SdOption::deserialize(const std::vector<uint8_t>& data, size_t& offset) {
    if (offset + 4 > data.size()) {
        return false;
    }

    type_ = static_cast<OptionType>(data[offset++]);
    offset++;  // Skip reserved byte

    length_ = (data[offset] << 8) | data[offset + 1];
    offset += 2;

    return true;
}

// IPv4EndpointOption implementation
std::vector<uint8_t> IPv4EndpointOption::serialize() const {
    std::vector<uint8_t> data = SdOption::serialize();

    // IPv4 Address (4 bytes)
    data.push_back((ipv4_address_ >> 24) & 0xFF);
    data.push_back((ipv4_address_ >> 16) & 0xFF);
    data.push_back((ipv4_address_ >> 8) & 0xFF);
    data.push_back(ipv4_address_ & 0xFF);

    // Reserved (1 byte)
    data.push_back(0);

    // Protocol (1 byte)
    data.push_back(protocol_);

    // Port (2 bytes)
    data.push_back((port_ >> 8) & 0xFF);
    data.push_back(port_ & 0xFF);

    // Update length (9 bytes: 4 address + 1 reserved + 1 protocol + 2 port + 1 base reserved)
    uint16_t length = 9;
    data[2] = (length >> 8) & 0xFF;
    data[3] = length & 0xFF;

    return data;
}

bool IPv4EndpointOption::deserialize(const std::vector<uint8_t>& data, size_t& offset) {
    if (!SdOption::deserialize(data, offset)) {
        return false;
    }

    if (offset + length_ > data.size()) {
        return false;
    }

    ipv4_address_ = (data[offset] << 24) | (data[offset + 1] << 16) |
                   (data[offset + 2] << 8) | data[offset + 3];
    offset += 5;  // Skip address + reserved
    protocol_ = data[offset++];
    port_ = (data[offset] << 8) | data[offset + 1];
    offset += 2;

    return true;
}

// IPv4MulticastOption implementation
std::vector<uint8_t> IPv4MulticastOption::serialize() const {
    std::vector<uint8_t> data = SdOption::serialize();

    // IPv4 Address (4 bytes)
    data.push_back((ipv4_address_ >> 24) & 0xFF);
    data.push_back((ipv4_address_ >> 16) & 0xFF);
    data.push_back((ipv4_address_ >> 8) & 0xFF);
    data.push_back(ipv4_address_ & 0xFF);

    // Reserved (1 byte)
    data.push_back(0);

    // Port (2 bytes)
    data.push_back((port_ >> 8) & 0xFF);
    data.push_back(port_ & 0xFF);

    // Update length (7 bytes: 4 address + 1 reserved + 2 port)
    uint16_t length = 7;
    data[2] = (length >> 8) & 0xFF;
    data[3] = length & 0xFF;

    return data;
}

bool IPv4MulticastOption::deserialize(const std::vector<uint8_t>& data, size_t& offset) {
    if (!SdOption::deserialize(data, offset)) {
        return false;
    }

    if (offset + length_ > data.size()) {
        return false;
    }

    ipv4_address_ = (data[offset] << 24) | (data[offset + 1] << 16) |
                   (data[offset + 2] << 8) | data[offset + 3];
    offset += 5;  // Skip address + reserved
    port_ = (data[offset] << 8) | data[offset + 1];
    offset += 2;

    return true;
}

// SdMessage implementation
void SdMessage::add_entry(std::unique_ptr<SdEntry> entry) {
    entries_.push_back(std::move(entry));
}

void SdMessage::add_option(std::unique_ptr<SdOption> option) {
    options_.push_back(std::move(option));
}

std::vector<uint8_t> SdMessage::serialize() const {
    std::vector<uint8_t> data;

    // SOME/IP SD Header (8 bytes)
    // Flags (1 byte)
    data.push_back(flags_);

    // Reserved (3 bytes) - we use 4 bytes total for reserved_
    data.push_back((reserved_ >> 16) & 0xFF);
    data.push_back((reserved_ >> 8) & 0xFF);
    data.push_back(reserved_ & 0xFF);

    // Length (4 bytes) - placeholder, will be filled later
    size_t length_offset = data.size();
    data.push_back(0);
    data.push_back(0);
    data.push_back(0);
    data.push_back(0);

    // Entries
    for (const auto& entry : entries_) {
        auto entry_data = entry->serialize();
        data.insert(data.end(), entry_data.begin(), entry_data.end());
    }

    // Options
    for (const auto& option : options_) {
        auto option_data = option->serialize();
        data.insert(data.end(), option_data.begin(), option_data.end());
    }

    // Update length (total length - 8 byte header)
    uint32_t total_length = data.size() - 8;
    data[length_offset] = (total_length >> 24) & 0xFF;
    data[length_offset + 1] = (total_length >> 16) & 0xFF;
    data[length_offset + 2] = (total_length >> 8) & 0xFF;
    data[length_offset + 3] = total_length & 0xFF;

    return data;
}

bool SdMessage::deserialize(const std::vector<uint8_t>& data) {
    if (data.size() < 8) {
        return false;
    }

    size_t offset = 0;

    // SOME/IP SD Header
    flags_ = data[offset++];
    reserved_ = (data[offset] << 16) | (data[offset + 1] << 8) | data[offset + 2];
    offset += 3;

    uint32_t length = (data[offset] << 24) | (data[offset + 1] << 16) |
                     (data[offset + 2] << 8) | data[offset + 3];
    offset += 4;

    if (offset + length > data.size()) {
        return false;
    }

    // Parse entries and options
    size_t entries_options_length = length;

    while (entries_options_length > 0) {
        if (offset + 1 > data.size()) {
            return false; // Not enough data for entry header
        }

        uint8_t entry_type = data[offset];
        EntryType type = static_cast<EntryType>(entry_type);

        // Determine entry type and create appropriate entry
        std::unique_ptr<SdEntry> entry;

        // Entry types 0x00-0x01 are service entries
        // Entry types 0x06-0x07 are eventgroup entries
        uint8_t raw_type = static_cast<uint8_t>(type);
        
        if (raw_type == 0x00 || raw_type == 0x01) {
            // FIND_SERVICE or OFFER_SERVICE
            entry = std::make_unique<ServiceEntry>();
        } else if (raw_type == 0x06 || raw_type == 0x07) {
            // SUBSCRIBE_EVENTGROUP or SUBSCRIBE_EVENTGROUP_ACK/NACK
            entry = std::make_unique<EventGroupEntry>();
        } else {
            // Unknown entry type, skip it
            offset++;
            if (entries_options_length > 0) {
                entries_options_length--;
            }
            continue;
        }

        if (entry && entry->deserialize(data, offset)) {
            entries_.push_back(std::move(entry));
            // Update remaining length based on current offset
            if (offset >= 8) {
                size_t parsed_length = offset - 8;  // Subtract header size
                if (parsed_length <= length) {
                    entries_options_length = length - parsed_length;
                } else {
                    entries_options_length = 0;
                }
            } else {
                entries_options_length = 0;
            }
        } else {
            // Failed to parse entry, stop parsing
            return false;
        }
    }

    return true;
}

} // namespace sd
} // namespace someip
