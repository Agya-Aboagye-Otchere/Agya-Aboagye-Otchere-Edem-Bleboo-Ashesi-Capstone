<?php

include "config_obj.php";

header('Content-Type: application/json');

$method = $_SERVER['REQUEST_METHOD'];

switch ($method) {
    case 'POST':
        $data = json_decode(file_get_contents('php://input'), true);
        $device_name = $data['device_name'];
    
        // Assuming $con is the database connection object
    
        // Prepare the SQL statement to insert the device name
        $stmt = $con->prepare('INSERT INTO Smart_devices (device_name) VALUES (?)');
        
        // Bind parameters to the prepared statement
        $stmt->bind_param("s", $device_name); // Use "s" for string type
        
        // Execute the prepared statement
        if ($stmt->execute()) {
            echo json_encode(['success_message' => 'Device added successfully']);
        } else {
            echo json_encode(['error_message' => 'Problem in adding new device']);
        }
        break;

    default:
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        break;
}
?>
