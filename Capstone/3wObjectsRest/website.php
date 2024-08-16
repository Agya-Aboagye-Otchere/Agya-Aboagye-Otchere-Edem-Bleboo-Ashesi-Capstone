<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Motor Data - Condition Monitoring of Electrical Machines</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1200px;
            margin: auto;
            padding: 20px;
        }
        h1 {
            background-color: #0056b3;
            color: white;
            padding: 15px;
            text-align: center;
            margin: 0;
            border-radius: 5px;
        }
        h2, h3 {
            color: #0056b3;
            text-align: center;
        }
        .form-container {
            text-align: center;
            margin-bottom: 20px;
            background-color: #e7f0ff;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #0056b3;
        }
        table {
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
            border-collapse: collapse;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            background-color: #ffffff;
            border-radius: 5px;
            overflow: hidden;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dddddd;
        }
        th {
            background-color: #0056b3;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .thermal-image {
            display: block;
            max-width: 500px;
            margin: 20px auto;
            border: 1px solid #dddddd;
            border-radius: 5px;
        }
        select {
            padding: 5px;
            font-size: 14px;
        }
        nav {
            background-color: #0056b3;
            padding: 10px 0;
            text-align: center;
        }
        nav a {
            color: white;
            text-decoration: none;
            margin: 0 15px;
            font-size: 18px;
        }
        nav a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>

<h1>Motor Data</h1>

<nav>
    <a href="home_page.php">Home</a>
    <a href="website.php">Motor Data</a>
    <a href="website2.php">Data Analysis</a>
    <a href="suggestion.php">Suggestion Page</a>
</nav>

<div class="container">

<?php
// Database connection parameters
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "capstone_data";
$port = 3307; // Adjust this if your MySQL server runs on a different port

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname, $port);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get selected motor ID from the form submission
$selected_motor_id = isset($_POST['motor_id']) ? intval($_POST['motor_id']) : 1;
?>

<div class="form-container">
    <form method="post" action="">
        <label for="motor_id">Select Motor:</label>
        <select name="motor_id" id="motor_id" onchange="this.form.submit()">
            <?php
            // Query to get motor devices
            $sql = "SELECT esp_ID, device_name FROM Smart_devices";
            $result = $conn->query($sql);

            if ($result->num_rows > 0) {
                while($row = $result->fetch_assoc()) {
                    $selected = ($row["esp_ID"] == $selected_motor_id) ? "selected" : "";
                    echo "<option value='" . $row["esp_ID"] . "' $selected>" . $row["device_name"] . "</option>";
                }
            }
            ?>
        </select>
        <noscript><input type="submit" value="Submit"></noscript>
    </form>
</div>

<h2>Motor Information</h2>
<table>
    <tr>
        <th>ID</th>
        <th>Name</th>
    </tr>
    <?php
    // Query to get motor information
    $sql = "SELECT esp_ID, device_name FROM Smart_devices WHERE esp_ID = $selected_motor_id";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<tr><td>" . $row["esp_ID"]. "</td><td>" . $row["device_name"]. "</td></tr>";
        }
    } else {
        echo "<tr><td colspan='2'>No motor found</td></tr>";
    }
    ?>
</table>

<h2>Data for Motor <?php echo $selected_motor_id; ?></h2>

<h3>Current Data</h3>
<table>
    <tr>
        <th>Time</th>
        <th>Current (A)</th>
    </tr>
    <?php
    // Query to get the last 5 current readings
    $sql = "SELECT DATE_FORMAT(reading_time, '%H:%i:%s') AS time, C FROM current_read WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<tr><td>" . $row["time"]. "</td><td>" . $row["C"]. "</td></tr>";
        }
    } else {
        echo "<tr><td colspan='2'>No data found</td></tr>";
    }
    ?>
</table>

<h3>Voltage Data</h3>
<table>
    <tr>
        <th>Time</th>
        <th>Voltage (V)</th>
    </tr>
    <?php
    // Query to get the last 5 voltage readings
    $sql = "SELECT DATE_FORMAT(reading_time, '%H:%i:%s') AS time, V FROM voltage WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<tr><td>" . $row["time"]. "</td><td>" . $row["V"]. "</td></tr>";
        }
    } else {
        echo "<tr><td colspan='2'>No data found</td></tr>";
    }
    ?>
</table>

<h3>Speed Data</h3>
<table>
    <tr>
        <th>Time</th>
        <th>Speed (RPM)</th>
    </tr>
    <?php
    // Query to get the last 5 speed readings
    $sql = "SELECT DATE_FORMAT(reading_time, '%H:%i:%s') AS time, S FROM speed WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<tr><td>" . $row["time"]. "</td><td>" . $row["S"]. "</td></tr>";
        }
    } else {
        echo "<tr><td colspan='2'>No data found</td></tr>";
    }
    ?>
</table>

<h3>Temperature Data</h3>
<table>
    <tr>
        <th>Time</th>
        <th>Temperature (&deg;C)</th>
    </tr>
    <?php
    // Query to get the last 5 temperature readings from the column 'temp'
    $sql = "SELECT DATE_FORMAT(reading_time, '%H:%i:%s') AS time, temp FROM temperature WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<tr><td>" . $row["time"]. "</td><td>" . $row["temp"]. "</td></tr>";
        }
    } else {
        echo "<tr><td colspan='2'>No data found</td></tr>";
    }
    ?>
</table>

<h3>Vibration Data</h3>
<table>
    <tr>
        <th>Time</th>
        <th>Ax</th>
        <th>Ay</th>
        <th>Az</th>
    </tr>
    <?php
    // Query to get the last 5 vibration readings
    $sql = "SELECT DATE_FORMAT(reading_time, '%H:%i:%s') AS time, ax, ay, az FROM vibration WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 5";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "<tr><td>" . $row["time"]. "</td><td>" . $row["ax"]. "</td><td>" . $row["ay"]. "</td><td>" . $row["az"]. "</td></tr>";
        }
    } else {
        echo "<tr><td colspan='4'>No data found</td></tr>";
    }
    ?>
</table>

<h3>Thermal Image</h3>
<?php
// Query to get the most recent thermal image
$sql = "SELECT image, DATE_FORMAT(reading_time, '%H:%i:%s') AS time FROM images WHERE esp_ID = $selected_motor_id ORDER BY reading_time DESC LIMIT 1";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        echo '<img src="data:image/jpeg;base64,'.base64_encode($row['image']).'" alt="Thermal Image" class="thermal-image" />';
    }
} else {
    echo "<p>No thermal image found</p>";
}
?>

</div>
</body>
</html>

<?php
$conn->close();
?>
