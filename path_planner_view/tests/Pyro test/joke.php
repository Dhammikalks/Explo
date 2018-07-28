

<?php
print(1);
$command = escapeshellcmd('./client.py SquirrelMaster 2>&1');
$output = shell_exec($command);
echo $output;
?>
