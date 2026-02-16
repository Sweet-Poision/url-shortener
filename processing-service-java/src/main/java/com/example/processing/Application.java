package com.example.processing;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@SpringBootApplication
public class Application {

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

@Service
class KafkaConsumerService {

    @Autowired
    private UrlRepository repository;

    private final ObjectMapper mapper = new ObjectMapper();

    @KafkaListener(topics = "url_events", groupId = "url-group")
    public void consume(String message) {
        try {
            // 1. Parse the JSON from Python
            var node = mapper.readTree(message);

            // 2. Create a Record
            UrlRecord record = new UrlRecord();
            record.setShortUrl(node.get("short_url").asText());
            record.setLongUrl(node.get("long_url").asText());

            // 3. Save to Postgres!
            repository.save(record);

            System.out.println("✅ SAVED TO POSTGRES: " + record.getShortUrl());
        } catch (Exception e) {
            System.err.println("❌ Failed to process event: " + e.getMessage());
        }
    }
}
