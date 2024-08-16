<?php

include "config_obj.php";

header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];

switch ($method) {
    case 'POST':
        $data = json_decode(file_get_contents('php://input'), true);
        $esp_ID = $data['esp_ID']; // id of device
        $temp = $data['temp'];    
        // Prepare the SQL statement to insert sensor readings
        $stmt = $con->prepare('INSERT INTO temperature (reading_time, esp_ID, temp) VALUES (CURRENT_TIMESTAMP, ?, ?)');
        
        // Bind parameters to the prepared statement
        // Assuming $esp_ID is the value of esp_ID corresponding to the device
        $stmt->bind_param("id", $esp_ID, $temp); 
        
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
