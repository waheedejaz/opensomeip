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

#include "sd/sd_client.h"
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

class SdClientImpl : public transport::ITransportListener {
public:
    SdClientImpl(const SdConfig& config)
        : config_(config),
          transport_(std::make_shared<transport::UdpTransport>(
              transport::Endpoint(config.unicast_address, config.unicast_port))),
          running_(false),
          next_request_id_(1) {

        transport_->set_listener(this);
    }

    ~SdClientImpl() {
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
        return true;
    }

    void shutdown() {
        if (!running_) {
            return;
        }

        running_ = false;

        // Clear all subscriptions and callbacks
        {
            std::scoped_lock lock(subscriptions_mutex_);
            service_subscriptions_.clear();
        }

        // Leave multicast group
        leave_multicast_group();

        transport_->stop();
    }

    bool find_service(uint16_t service_id, FindServiceCallback callback,
                     std::chrono::milliseconds timeout) {

        if (!running_) {
            return false;
        }

        // Create find service entry
        auto find_entry = std::make_unique<ServiceEntry>(EntryType::FIND_SERVICE);
        find_entry->set_service_id(service_id);
        find_entry->set_instance_id(0xFFFF);  // Find any instance
        find_entry->set_major_version(0xFF);  // Any version
        find_entry->set_ttl(3);  // 3 seconds TTL for find

        // Create SD message
        SdMessage sd_message;
        sd_message.add_entry(std::move(find_entry));

        // Create SOME/IP message for SD (service ID 0xFFFF)
        Message someip_message(MessageId(0xFFFF, 0x0000), RequestId(0x0000, 0x0000),
                              MessageType::NOTIFICATION, ReturnCode::E_OK);
        someip_message.set_payload(sd_message.serialize());

        // Send multicast find message
        transport::Endpoint multicast_endpoint(config_.multicast_address, config_.multicast_port);
        if (transport_->send_message(someip_message, multicast_endpoint) != Result::SUCCESS) {
            return false;
        }

        // Store callback for responses
        uint32_t request_id = next_request_id_++;
        {
            std::scoped_lock lock(pending_finds_mutex_);
            pending_finds_[request_id] = {
                service_id, std::move(callback),
                std::chrono::steady_clock::now(),
                timeout.count() == 0 ? std::chrono::milliseconds(5000) : timeout
            };
        }

        return true;
    }

    bool subscribe_service(uint16_t service_id,
                          ServiceAvailableCallback available_callback,
                          ServiceUnavailableCallback unavailable_callback) {

        std::scoped_lock lock(subscriptions_mutex_);

        // Check if already subscribed
        bool already_exists = service_subscriptions_.count(service_id) > 0;
        if (!already_exists) {
            service_subscriptions_[service_id] = {
                std::move(available_callback),
                std::move(unavailable_callback)
            };
        }
        return !already_exists;
    }

    bool unsubscribe_service(uint16_t service_id) {
        std::scoped_lock lock(subscriptions_mutex_);
        return service_subscriptions_.erase(service_id) > 0;
    }

    bool subscribe_eventgroup(uint16_t service_id, uint16_t instance_id, uint16_t eventgroup_id) {
        if (!running_) {
            return false;
        }

        // Create subscribe event group entry
        auto subscribe_entry = std::make_unique<EventGroupEntry>(EntryType::SUBSCRIBE_EVENTGROUP);
        subscribe_entry->set_service_id(service_id);
        subscribe_entry->set_instance_id(instance_id);
        subscribe_entry->set_eventgroup_id(eventgroup_id);
        subscribe_entry->set_major_version(0x01);  // Version 1
        subscribe_entry->set_ttl(3600);  // 1 hour TTL

        // Create SD message
        SdMessage sd_message;
        sd_message.add_entry(std::move(subscribe_entry));

        // Add IPv4 endpoint option (client's unicast address)
        auto endpoint_option = std::make_unique<IPv4EndpointOption>();
        // TODO: Set actual endpoint information
        sd_message.add_option(std::move(endpoint_option));

        // Create SOME/IP message for SD
        Message someip_message(MessageId(0xFFFF, 0x0000), RequestId(0x0000, 0x0000),
                              MessageType::NOTIFICATION, ReturnCode::E_OK);
        someip_message.set_payload(sd_message.serialize());

        // Send multicast message
        transport::Endpoint multicast_endpoint(config_.multicast_address, config_.multicast_port);
        return transport_->send_message(someip_message, multicast_endpoint) == Result::SUCCESS;
    }

    bool unsubscribe_eventgroup(uint16_t service_id, uint16_t instance_id, uint16_t eventgroup_id) {
        if (!running_) {
            return false;
        }

        // Create unsubscribe event group entry (TTL = 0)
        auto unsubscribe_entry = std::make_unique<EventGroupEntry>(EntryType::STOP_SUBSCRIBE_EVENTGROUP);
        unsubscribe_entry->set_service_id(service_id);
        unsubscribe_entry->set_instance_id(instance_id);
        unsubscribe_entry->set_eventgroup_id(eventgroup_id);
        unsubscribe_entry->set_major_version(0x01);
        unsubscribe_entry->set_ttl(0);  // TTL = 0 means unsubscribe

        // Create SD message
        SdMessage sd_message;
        sd_message.add_entry(std::move(unsubscribe_entry));

        // Create SOME/IP message for SD
        Message someip_message(MessageId(0xFFFF, 0x0000), RequestId(0x0000, 0x0000),
                              MessageType::NOTIFICATION, ReturnCode::E_OK);
        someip_message.set_payload(sd_message.serialize());

        // Send multicast message
        transport::Endpoint multicast_endpoint(config_.multicast_address, config_.multicast_port);
        return transport_->send_message(someip_message, multicast_endpoint) == Result::SUCCESS;
    }

    std::vector<ServiceInstance> get_available_services(uint16_t service_id) const {
        std::scoped_lock lock(available_services_mutex_);
        std::vector<ServiceInstance> result;

        for (const auto& service : available_services_) {
            if (service_id == 0 || service.service_id == service_id) {
                result.push_back(service);
            }
        }

        return result;
    }

    bool is_ready() const {
        return running_ && transport_->is_connected();
    }

    SdClient::Statistics get_statistics() const {
        // TODO: Implement statistics tracking
        return SdClient::Statistics{};
    }

private:
    struct ServiceSubscription {
        ServiceAvailableCallback available_callback;
        ServiceUnavailableCallback unavailable_callback;
    };

    struct PendingFind {
        uint16_t service_id;
        FindServiceCallback callback;
        std::chrono::steady_clock::time_point start_time;
        std::chrono::milliseconds timeout;
    };

    bool join_multicast_group() {
        // TODO: Implement multicast group joining
        // This would typically involve setting socket options
        return true;
    }

    void leave_multicast_group() {
        // TODO: Implement multicast group leaving
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
        process_sd_entries(sd_message);
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

    void process_sd_entries(const SdMessage& message) {
        for (const auto& entry : message.get_entries()) {
            switch (entry->get_type()) {
                case EntryType::OFFER_SERVICE:
                    // Check TTL to distinguish between offer and stop offer
                    if (entry->get_ttl() == 0) {
                        handle_service_stop_offer(*static_cast<const ServiceEntry*>(entry.get()));
                    } else {
                        handle_service_offer(*static_cast<const ServiceEntry*>(entry.get()));
                    }
                    break;
                default:
                    // Other entry types not handled by client
                    break;
            }
        }
    }

    void handle_service_offer(const ServiceEntry& entry) {
        ServiceInstance instance;
        instance.service_id = entry.get_service_id();
        instance.instance_id = entry.get_instance_id();
        instance.major_version = entry.get_major_version();
        instance.minor_version = 0;  // Not in basic offer
        instance.ttl_seconds = entry.get_ttl();

        // TODO: Extract endpoint information from options

        // Update available services
        {
            std::scoped_lock lock(available_services_mutex_);
            auto it = std::find_if(available_services_.begin(), available_services_.end(),
                [&](const ServiceInstance& svc) {
                    return svc.service_id == instance.service_id &&
                           svc.instance_id == instance.instance_id;
                });

            if (it == available_services_.end()) {
                available_services_.push_back(instance);
            } else {
                *it = instance;  // Update existing
            }
        }

        // Notify subscribers
        std::scoped_lock lock(subscriptions_mutex_);
        auto sub_it = service_subscriptions_.find(instance.service_id);
        if (sub_it != service_subscriptions_.end() && sub_it->second.available_callback) {
            sub_it->second.available_callback(instance);
        }

        // Check for pending finds
        {
            std::scoped_lock lock(pending_finds_mutex_);
            for (auto it = pending_finds_.begin(); it != pending_finds_.end(); ) {
                if (it->second.service_id == instance.service_id) {
                    if (it->second.callback) {
                        std::vector<ServiceInstance> found_services = {instance};
                        it->second.callback(found_services);
                    }
                    it = pending_finds_.erase(it);
                } else {
                    ++it;
                }
            }
        }
    }

    void handle_service_stop_offer(const ServiceEntry& entry) {
        ServiceInstance instance;
        instance.service_id = entry.get_service_id();
        instance.instance_id = entry.get_instance_id();

        // Remove from available services
        {
            std::scoped_lock lock(available_services_mutex_);
            auto it = std::remove_if(available_services_.begin(), available_services_.end(),
                [&](const ServiceInstance& svc) {
                    return svc.service_id == instance.service_id &&
                           svc.instance_id == instance.instance_id;
                });
            available_services_.erase(it, available_services_.end());
        }

        // Notify subscribers
        std::scoped_lock lock(subscriptions_mutex_);
        auto sub_it = service_subscriptions_.find(instance.service_id);
        if (sub_it != service_subscriptions_.end() && sub_it->second.unavailable_callback) {
            sub_it->second.unavailable_callback(instance);
        }
    }

    SdConfig config_;
    std::shared_ptr<transport::UdpTransport> transport_;

    std::unordered_map<uint16_t, ServiceSubscription> service_subscriptions_;
    mutable std::mutex subscriptions_mutex_;

    std::vector<ServiceInstance> available_services_;
    mutable std::mutex available_services_mutex_;

    std::unordered_map<uint32_t, PendingFind> pending_finds_;
    mutable std::mutex pending_finds_mutex_;

    std::atomic<uint32_t> next_request_id_;
    std::atomic<bool> running_;
};

// SdClient implementation
SdClient::SdClient(const SdConfig& config)
    : impl_(std::make_unique<SdClientImpl>(config)) {
}

SdClient::~SdClient() = default;

bool SdClient::initialize() {
    return impl_->initialize();
}

void SdClient::shutdown() {
    impl_->shutdown();
}

bool SdClient::find_service(uint16_t service_id, FindServiceCallback callback,
                           std::chrono::milliseconds timeout) {
    return impl_->find_service(service_id, std::move(callback), timeout);
}

bool SdClient::subscribe_service(uint16_t service_id,
                                ServiceAvailableCallback available_callback,
                                ServiceUnavailableCallback unavailable_callback) {
    return impl_->subscribe_service(service_id, std::move(available_callback),
                                   std::move(unavailable_callback));
}

bool SdClient::unsubscribe_service(uint16_t service_id) {
    return impl_->unsubscribe_service(service_id);
}

bool SdClient::subscribe_eventgroup(uint16_t service_id, uint16_t instance_id, uint16_t eventgroup_id) {
    return impl_->subscribe_eventgroup(service_id, instance_id, eventgroup_id);
}

bool SdClient::unsubscribe_eventgroup(uint16_t service_id, uint16_t instance_id, uint16_t eventgroup_id) {
    return impl_->unsubscribe_eventgroup(service_id, instance_id, eventgroup_id);
}

std::vector<ServiceInstance> SdClient::get_available_services(uint16_t service_id) const {
    return impl_->get_available_services(service_id);
}

bool SdClient::is_ready() const {
    return impl_->is_ready();
}

SdClient::Statistics SdClient::get_statistics() const {
    return impl_->get_statistics();
}

} // namespace sd
} // namespace someip
