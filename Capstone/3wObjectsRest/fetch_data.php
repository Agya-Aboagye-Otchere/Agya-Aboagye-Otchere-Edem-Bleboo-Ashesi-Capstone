<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "capstone_data";
$port = 3307;

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get selected motor ID from the request
$selected_motor_id = isset($_GET['motor_id']) ? intval($_GET['motor_id']) : 1;

$response = [];

// Fetch current data
$sql = "SELECT TIME(reading_time) AS reading_time, C FROM current_read WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
$result = $conn->query($sql);
$current_data = [];
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $current_data[] = $row;
    }
}
$response['current_data'] = $current_data;

// Fetch voltage data
$sql = "SELECT TIME(reading_time) AS reading_time, V FROM voltage WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
$result = $conn->query($sql);
$voltage_data = [];
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $voltage_data[] = $row;
    }
}
$response['voltage_data'] = $voltage_data;

// Fetch speed data
$sql = "SELECT TIME(reading_time) AS reading_time, S FROM speed WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
$result = $conn->query($sql);
$speed_data = [];
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $speed_data[] = $row;
    }
}
$response['speed_data'] = $speed_data;

// Fetch vibration data
$sql = "SELECT TIME(reading_time) AS reading_time, ax, ay, az FROM vibration WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
$result = $conn->query($sql);
$vibration_data = [];
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $vibration_data[] = $row;
    }
}
$response['vibration_data'] = $vibration_data;

// Fetch the latest thermal image
$sql = "SELECT image FROM images WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 1";
$result = $conn->query($sql);
$thermal_image = null;
if ($result->num_rows > 0) {
    $row = $result->fetch_assoc();
    $thermal_image = base64_encode($row['image']);
}
$response['thermal_image'] = $thermal_image;

header('Content-Type: application/json');
echo json_encode($response);

$conn->close();
?>
