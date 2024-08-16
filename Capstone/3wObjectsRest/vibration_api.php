<?php

include "config_obj.php";

header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];

switch ($method) {
    case 'POST':
        $data = json_decode(file_get_contents('php://input'), true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            echo json_encode(['error_message' => 'Invalid JSON input']);
            break;
        }

        $esp_ID = $data['esp_ID']; // id of device
        $ax = $data['ax'] ?? null;
        $ay = $data['ay'] ?? null;
        $az = $data['az'] ?? null;

        if ($ax === null || $ay === null || $az === null) {
            echo json_encode(['error_message' => 'Missing required parameters']);
            break;
        }

        // Prepare the SQL statement to insert sensor readings
        $stmt = $con->prepare('INSERT INTO vibration (reading_time, esp_ID, ax, ay, az) VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)');
        
        // Bind parameters to the prepared statement
        $stmt->bind_param("iddd", $esp_ID, $ax, $ay, $az); 
        
        // Execute the prepared statement
        if ($stmt->execute()) {
            echo json_encode(['success_message' => 'Sensor readings added successfully']);
        } else {
            echo json_encode(['error_message' => 'Problem in adding new sensor readings']);
        }
        break;

    default:
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        break;
}
?>
