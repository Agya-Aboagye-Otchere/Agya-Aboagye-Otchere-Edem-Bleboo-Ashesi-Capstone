<?php

// Database configuration
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "capstone_data";
$port = 3307;  // Use the correct port

// Create connection
$con = new mysqli($servername, $username, $password, $dbname, $port);

// Check connection
if ($con->connect_error) {
    die("Connection failed: " . $con->connect_error);
}

?>
