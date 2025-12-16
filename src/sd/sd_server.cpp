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

#include "sd/sd_server.h"
#include "sd/sd_message.h"
#include "transport/udp_transport.h"
#include "transport/endpoint.h"
#include "transport/transport.h"
#include "someip/message.h"
#include <unordered_map>
#include <mutex>
#include <atomic>
#include <thread>
#include <chrono>
#include <algorithm>

namespace someip {
namespace sd {

class SdServerImpl : public transport::ITransportListener {
public:
    SdServerImpl(const SdConfig& config)
        : config_(config),
          transport_(std::make_shared<transport::UdpTransport>(
              transport::Endpoint(config.unicast_address, config.unicast_port))),
          running_(false),
          next_offer_delay_(config.initial_delay) {

        transport_->set_listener(this);
    }

    ~SdServerImpl() {
        shutdown();
    }

    bool initialize() {
        if (running_) {
            return true;
        }

        if (transport_->start() != Result::SUCCESS) {
            return false;
        }

        // Join multicast group for SD messages
        if (!join_multicast_group()) {
            transport_->stop();
            return false;
        }

        running_ = true;

        // Start offer timer
        start_offer_timer();

        return true;
    }

    void shutdown() {
        if (!running_) {
            return;
        }

        running_ = false;

        // Stop offer timer
        stop_offer_timer();

        // Send stop offer messages for all services
        send_stop_offer_messages();

        // Clear offered services
        std::scoped_lock lock(offered_services_mutex_);
        offered_services_.clear();

        // Leave multicast group
        leave_multicast_group();

        transport_->stop();
    }

    bool offer_service(const ServiceInstance& instance,
                      const std::string& unicast_endpoint,
                      const std::string& multicast_endpoint) {

        std::scoped_lock lock(offered_services_mutex_);

        // Check if service already offered
        auto it = std::find_if(offered_services_.begin(), offered_services_.end(),
            [&](const OfferedService& svc) {
                return svc.instance.service_id == instance.service_id &&
                       svc.instance.instance_id == instance.instance_id;
            });

        if (it != offered_services_.end()) {
            return false;  // Already offered
        }

        OfferedService offered;
        offered.instance = instance;
        offered.unicast_endpoint = unicast_endpoint;
        offered.multicast_endpoint = multicast_endpoint;
        offered.last_offer_time = std::chrono::steady_clock::now();

        offered_services_.push_back(std::move(offered));

        // Send initial offer immediately
        send_service_offer(offered_services_.back());

        return true;
    }

    bool stop_offer_service(uint16_t service_id, uint16_t instance_id) {
        std::scoped_lock lock(offered_services_mutex_);

        auto it = std::find_if(offered_services_.begin(), offered_services_.end(),
            [&](const OfferedService& svc) {
                return svc.instance.service_id == service_id &&
                       svc.instance.instance_id == instance_id;
            });

        if (it == offered_services_.end()) {
            return false;
        }

        // Send stop offer message
        send_service_stop_offer(*it);

        offered_services_.erase(it);
        return true;
    }

    bool update_service_ttl(uint16_t service_id, uint16_t instance_id, uint32_t ttl_seconds) {
        std::scoped_lock lock(offered_services_mutex_);

        auto it = std::find_if(offered_services_.begin(), offered_services_.end(),
            [&](const OfferedService& svc) {
                return svc.instance.service_id == service_id &&
                       svc.instance.instance_id == instance_id;
            });

        if (it == offered_services_.end()) {
            return false;
        }

        it->instance.ttl_seconds = ttl_seconds;
        return true;
    }

    bool handle_eventgroup_subscription(uint16_t service_id, uint16_t instance_id,
                                       uint16_t eventgroup_id, const std::string& client_address,
                                       bool acknowledge) {

        // Create subscription response
        auto response_entry = std::make_unique<EventGroupEntry>(
            acknowledge ? EntryType::SUBSCRIBE_EVENTGROUP_ACK : EntryType::SUBSCRIBE_EVENTGROUP_NACK);
        response_entry->set_service_id(service_id);
        response_entry->set_instance_id(instance_id);
        response_entry->set_eventgroup_id(eventgroup_id);
        response_entry->set_major_version(0x01);
        response_entry->set_ttl(acknowledge ? 3600 : 0);  // TTL or 0 for NACK

        SdMessage response_message;
        response_message.add_entry(std::move(response_entry));

        // TODO: Add endpoint option for the service

        // Send unicast response to client
        // TODO: Parse client_address and create endpoint

        return true;  // Simplified - assume success
    }

    std::vector<ServiceInstance> get_offered_services() const {
        std::scoped_lock lock(offered_services_mutex_);
        std::vector<ServiceInstance> result;

        for (const auto& service : offered_services_) {
            result.push_back(service.instance);
        }

        return result;
    }

    bool is_ready() const {
        return running_ && transport_->is_connected();
    }

    SdServer::Statistics get_statistics() const {
        // TODO: Implement statistics tracking
        return SdServer::Statistics{};
    }

private:
    struct OfferedService {
        ServiceInstance instance;
        std::string unicast_endpoint;
        std::string multicast_endpoint;
        std::chrono::steady_clock::time_point last_offer_time;
    };

    bool join_multicast_group() {
        // TODO: Implement multicast group joining
        return true;
    }

    void leave_multicast_group() {
        // TODO: Implement multicast group leaving
    }

    void start_offer_timer() {
        if (offer_timer_thread_.joinable()) {
            return;
        }

        offer_timer_thread_ = std::thread([this]() {
            while (running_) {
                std::this_thread::sleep_for(next_offer_delay_);

                if (!running_) {
                    break;
                }

                // Send periodic offers
                send_periodic_offers();

                // Update next delay (exponential backoff with max)
                if (next_offer_delay_ < config_.repetition_max) {
                    next_offer_delay_ = std::chrono::milliseconds(
                        std::min(next_offer_delay_.count() * config_.repetition_multiplier,
                                config_.repetition_max.count()));
                }
            }
        });
    }

    void stop_offer_timer() {
        if (offer_timer_thread_.joinable()) {
            offer_timer_thread_.join();
        }
    }

    void send_periodic_offers() {
        std::scoped_lock lock(offered_services_mutex_);

        auto now = std::chrono::steady_clock::now();
        for (auto& service : offered_services_) {
            auto time_since_last_offer = std::chrono::duration_cast<std::chrono::milliseconds>(
                now - service.last_offer_time);

            if (time_since_last_offer >= config_.cyclic_offer) {
                send_service_offer(service);
                service.last_offer_time = now;
            }
        }
    }

    void send_stop_offer_messages() {
        std::scoped_lock lock(offered_services_mutex_);

        for (const auto& service : offered_services_) {
            send_service_stop_offer(service);
        }
    }

    void send_service_offer(const OfferedService& service) {
        // Create offer service entry
        auto offer_entry = std::make_unique<ServiceEntry>(EntryType::OFFER_SERVICE);
        offer_entry->set_service_id(service.instance.service_id);
        offer_entry->set_instance_id(service.instance.instance_id);
        offer_entry->set_major_version(service.instance.major_version);
        offer_entry->set_ttl(service.instance.ttl_seconds);

        SdMessage sd_message;
        sd_message.add_entry(std::move(offer_entry));

        // Add IPv4 endpoint option
        auto endpoint_option = std::make_unique<IPv4EndpointOption>();
        // TODO: Parse and set actual endpoint information
        sd_message.add_option(std::move(endpoint_option));

        // Create SOME/IP message for SD
        Message someip_message(MessageId(0xFFFF, 0x0000), RequestId(0x0000, 0x0000),
                              MessageType::NOTIFICATION, ReturnCode::E_OK);
        someip_message.set_payload(sd_message.serialize());

        // Send multicast offer
        transport::Endpoint multicast_endpoint(config_.multicast_address, config_.multicast_port);
        Result result = transport_->send_message(someip_message, multicast_endpoint);
        if (result != Result::SUCCESS) {
            // Log error or handle failure
        }
    }

    void send_service_stop_offer(const OfferedService& service) {
        // Create stop offer service entry
        auto stop_entry = std::make_unique<ServiceEntry>(EntryType::STOP_OFFER_SERVICE);
        stop_entry->set_service_id(service.instance.service_id);
        stop_entry->set_instance_id(service.instance.instance_id);
        stop_entry->set_major_version(service.instance.major_version);
        stop_entry->set_ttl(0);  // TTL = 0 means stop offering

        SdMessage sd_message;
        sd_message.add_entry(std::move(stop_entry));

        // Create SOME/IP message for SD
        Message someip_message(MessageId(0xFFFF, 0x0000), RequestId(0x0000, 0x0000),
                              MessageType::NOTIFICATION, ReturnCode::E_OK);
        someip_message.set_payload(sd_message.serialize());

        // Send multicast stop offer
        transport::Endpoint multicast_endpoint(config_.multicast_address, config_.multicast_port);
        Result result = transport_->send_message(someip_message, multicast_endpoint);
        if (result != Result::SUCCESS) {
            // Log error or handle failure
        }
    }

    void on_message_received(MessagePtr message, const transport::Endpoint& sender) override {
        // Check if this is an SD message (service ID 0xFFFF)
        if (message->get_service_id() != 0xFFFF) {
            return;
        }

        // Parse SD message
        SdMessage sd_message;
        if (!sd_message.deserialize(message->get_payload())) {
            return;
        }

        // Process SD entries
        process_sd_entries(sd_message, sender);
    }

    void on_connection_lost(const transport::Endpoint& endpoint) override {
        // TODO: Handle connection loss
    }

    void on_connection_established(const transport::Endpoint& endpoint) override {
        // TODO: Handle connection establishment
    }

    void on_error(Result error) override {
        // TODO: Handle transport errors
    }

    void process_sd_entries(const SdMessage& message, const transport::Endpoint& sender) {
        for (const auto& entry : message.get_entries()) {
            switch (entry->get_type()) {
                case EntryType::FIND_SERVICE:
                    handle_find_service(*static_cast<const ServiceEntry*>(entry.get()), sender);
                    break;
                case EntryType::SUBSCRIBE_EVENTGROUP:
                    handle_eventgroup_subscription_request(
                        *static_cast<const EventGroupEntry*>(entry.get()), sender);
                    break;
                default:
                    // Other entry types not handled by server
                    break;
            }
        }
    }

    void handle_find_service(const ServiceEntry& find_entry, const transport::Endpoint& sender) {
        std::scoped_lock lock(offered_services_mutex_);

        // Check if we offer the requested service
        for (const auto& service : offered_services_) {
            if (service.instance.service_id == find_entry.get_service_id() &&
                (find_entry.get_instance_id() == 0xFFFF ||  // Any instance
                 service.instance.instance_id == find_entry.get_instance_id())) {

                // Send unicast offer to the finder
                send_service_offer_to_client(service, sender);
                break;
            }
        }
    }

    void handle_eventgroup_subscription_request(const EventGroupEntry& subscription_entry,
                                               const transport::Endpoint& sender) {
        // TODO: Validate service and event group
        // For now, acknowledge all subscription requests

        handle_eventgroup_subscription(
            subscription_entry.get_service_id(),
            subscription_entry.get_instance_id(),
            subscription_entry.get_eventgroup_id(),
            "",  // TODO: Extract client address from sender
            true  // Acknowledge
        );
    }

    void send_service_offer_to_client(const OfferedService& service, const transport::Endpoint& client) {
        // Create unicast offer message (similar to multicast but unicast)
        auto offer_entry = std::make_unique<ServiceEntry>(EntryType::OFFER_SERVICE);
        offer_entry->set_service_id(service.instance.service_id);
        offer_entry->set_instance_id(service.instance.instance_id);
        offer_entry->set_major_version(service.instance.major_version);
        offer_entry->set_ttl(service.instance.ttl_seconds);

        SdMessage sd_message;
        sd_message.set_unicast(true);  // Unicast response
        sd_message.add_entry(std::move(offer_entry));

        // Add IPv4 endpoint option
        auto endpoint_option = std::make_unique<IPv4EndpointOption>();
        // TODO: Set actual endpoint information
        sd_message.add_option(std::move(endpoint_option));

        // Create SOME/IP message for SD
        Message someip_message(MessageId(0xFFFF, 0x0000), RequestId(0x0000, 0x0000),
                              MessageType::NOTIFICATION, ReturnCode::E_OK);
        someip_message.set_payload(sd_message.serialize());

        // Send unicast offer to client
        Result result = transport_->send_message(someip_message, client);
        if (result != Result::SUCCESS) {
            // Log error or handle failure
        }
    }

    SdConfig config_;
    std::shared_ptr<transport::UdpTransport> transport_;

    std::vector<OfferedService> offered_services_;
    mutable std::mutex offered_services_mutex_;

    std::thread offer_timer_thread_;
    std::chrono::milliseconds next_offer_delay_;
    std::atomic<bool> running_;
};

// SdServer implementation
SdServer::SdServer(const SdConfig& config)
    : impl_(std::make_unique<SdServerImpl>(config)) {
}

SdServer::~SdServer() = default;

bool SdServer::initialize() {
    return impl_->initialize();
}

void SdServer::shutdown() {
    impl_->shutdown();
}

bool SdServer::offer_service(const ServiceInstance& instance,
                            const std::string& unicast_endpoint,
                            const std::string& multicast_endpoint) {
    return impl_->offer_service(instance, unicast_endpoint, multicast_endpoint);
}

bool SdServer::stop_offer_service(uint16_t service_id, uint16_t instance_id) {
    return impl_->stop_offer_service(service_id, instance_id);
}

bool SdServer::update_service_ttl(uint16_t service_id, uint16_t instance_id, uint32_t ttl_seconds) {
    return impl_->update_service_ttl(service_id, instance_id, ttl_seconds);
}

bool SdServer::handle_eventgroup_subscription(uint16_t service_id, uint16_t instance_id,
                                             uint16_t eventgroup_id, const std::string& client_address,
                                             bool acknowledge) {
    return impl_->handle_eventgroup_subscription(service_id, instance_id, eventgroup_id,
                                                client_address, acknowledge);
}

std::vector<ServiceInstance> SdServer::get_offered_services() const {
    return impl_->get_offered_services();
}

bool SdServer::is_ready() const {
    return impl_->is_ready();
}

SdServer::Statistics SdServer::get_statistics() const {
    return impl_->get_statistics();
}

} // namespace sd
} // namespace someip
